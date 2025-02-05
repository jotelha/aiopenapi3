"""
Tests parsing specs
"""
import dataclasses
import sys
import uuid

if sys.version_info >= (3, 9):
    pass
else:
    import pathlib3x as pathlib

import pytest

from pydantic import ValidationError
from aiopenapi3 import OpenAPI, SpecError, ReferenceResolutionError, FileSystemLoader

URLBASE = "/"


def test_parse_from_yaml(petstore_expanded):
    """
    Tests that we can parse a valid yaml file
    """
    spec = OpenAPI(URLBASE, petstore_expanded)


def test_parsing_fails(broken):
    """
    Tests that broken specs fail to parse
    """
    with pytest.raises(ValidationError) as e:
        spec = OpenAPI(URLBASE, broken)


def test_parsing_broken_refernece(broken_reference):
    """
    Tests that parsing fails correctly when a reference is broken
    """
    with pytest.raises(ReferenceResolutionError):
        spec = OpenAPI(URLBASE, broken_reference)


def test_parsing_wrong_parameter_name(has_bad_parameter_name):
    """
    Tests that parsing fails if parameter name for path parameters aren't
    actually in the path.
    """
    with pytest.raises(SpecError, match="Parameter name not found in path: different"):
        spec = OpenAPI(URLBASE, has_bad_parameter_name)


def test_parsing_dupe_operation_id(dupe_op_id):
    """
    Tests that duplicate operation Ids are an error
    """
    with pytest.raises(SpecError, match="Duplicate operationId dupe"):
        spec = OpenAPI(URLBASE, dupe_op_id)


def test_parsing_parameter_name_with_underscores(parameter_with_underscores):
    """
    Tests that path parameters with underscores in them are accepted
    """
    spec = OpenAPI(URLBASE, parameter_with_underscores)


def test_object_example(obj_example_expanded):
    """
    Tests that `example` exists.
    """
    spec = OpenAPI(URLBASE, obj_example_expanded)
    schema = spec.paths["/check-dict"].get.responses["200"].content["application/json"].schema_
    assert isinstance(schema.example, dict)
    assert isinstance(schema.example["real"], float)

    schema = spec.paths["/check-str"].get.responses["200"].content["text/plain"]
    assert isinstance(schema.example, str)


def test_parsing_float_validation(float_validation_expanded):
    """
    Tests that `minimum` and similar validators work with floats.
    """
    spec = OpenAPI(URLBASE, float_validation_expanded)
    properties = spec.paths["/foo"].get.responses["200"].content["application/json"].schema_.properties

    assert isinstance(properties["integer"].minimum, int)
    assert isinstance(properties["integer"].maximum, int)
    assert isinstance(properties["real"].minimum, float)
    assert isinstance(properties["real"].maximum, float)


def test_parsing_with_links(with_links):
    """
    Tests that "links" parses correctly
    """
    spec = OpenAPI(URLBASE, with_links)

    assert "exampleWithOperationRef" in spec.components.links
    assert spec.components.links["exampleWithOperationRef"].operationRef == "/with-links"

    response_a = spec.paths["/with-links"].get.responses["200"]
    assert "exampleWithOperationId" in response_a.links
    assert response_a.links["exampleWithOperationId"].operationId == "withLinksTwo"

    response_b = spec.paths["/with-links-two/{param}"].get.responses["200"]
    assert "exampleWithRef" in response_b.links
    assert response_b.links["exampleWithRef"]._target == spec.components.links["exampleWithOperationRef"]


def test_parsing_broken_links(with_broken_links):
    """
    Tests that broken "links" values error properly
    """
    with pytest.raises(ValidationError) as e:
        spec = OpenAPI(URLBASE, with_broken_links)

    assert all(
        [
            i in str(e.value)
            for i in [
                "operationId and operationRef are mutually exclusive, only one of them is allowed",
                "operationId and operationRef are mutually exclusive, one of them must be specified",
            ]
        ]
    )


def test_securityparameters(with_securityparameters):
    spec = OpenAPI(URLBASE, with_securityparameters)


def test_callback(with_callback):
    spec = OpenAPI(URLBASE, with_callback)


@dataclasses.dataclass
class _Version:
    major: int
    minor: int
    patch: int = 0

    def __str__(self):
        if self.major == 3:
            return f'openapi: "{self.major}.{self.minor}.{self.patch}"'
        else:
            return f'swagger: "{self.major}.{self.minor}"'


@pytest.fixture(scope="session", params=[_Version(2, 0), _Version(3, 0, 3), _Version(3, 1, 0)])
def openapi_version(request):
    return request.param


def test_extended_paths(openapi_version):
    DOC = f"""{openapi_version}
info:
  title: ''
  version: 0.0.0
paths:
    x-codegen-contextRoot: /apis/registry/v2
"""
    api = OpenAPI.loads("test.yaml", DOC)
    print(api)


def test_allof_discriminator(with_allof_discriminator):
    api = OpenAPI(URLBASE, with_allof_discriminator)

    schema = api.components.schemas["Object1"]
    type_ = schema.get_type()
    obj1 = type_.construct(
        type="obj1",
        subtypeProperties=schema.properties["subtypeProperties"].get_type().construct(property1a="1a", property1b="1b"),
        id=uuid.uuid4(),
    )
    data = obj1.json()
    obj1_ = api.components.schemas["ObjectBaseType"].get_type().parse_raw(data)


def test_enum(with_enum):
    import linode_test

    api = OpenAPI(URLBASE, with_enum, plugins=[linode_test.LinodeDiscriminators()])
    import datetime

    s = api.components.schemas["PaymentMethod"]
    t = s.get_type()
    pay = t(__root__=dict(created=datetime.datetime.now(), id=5, is_default=True, type="google_pay", data=None))
    data = pay.json()
    pay_ = t.parse_raw(data)
    assert pay == pay_

    pay = t(__root__=dict(created=datetime.datetime.now(), id=5, is_default=True, type="google_pay", data=None))

    with pytest.raises(ValidationError):
        pay = t(__root__=dict(created=datetime.datetime.now(), id=5, is_default=True, type="no_pay", data=None))

    pp = api.components.schemas["PayPalData"].get_type()(email="a@b.de", paypal_id="1")
    assert pp.dict()["type"] == "paypal"
