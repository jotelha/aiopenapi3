from __future__ import annotations
import sys

"""
This file tests that $ref resolution works as expected, and that
allOfs are populated as expected as well.
"""

if sys.version_info >= (3, 8):
    import typing
else:
    # fot typing.get_origin
    import typing_extensions as typing


import dataclasses
import pytest
from aiopenapi3 import OpenAPI

from pydantic.main import ModelMetaclass


def test_ref_resolution(petstore_expanded_spec):
    """
    Tests that $refs are resolved as we expect them to be
    """
    from aiopenapi3.v30.schemas import Schema

    ref = petstore_expanded_spec.paths["/pets"].get.responses["default"].content["application/json"].schema_

    assert type(ref._target) == Schema
    assert ref.type == "object"
    assert len(ref.properties) == 2
    assert "code" in ref.properties
    assert "message" in ref.properties
    assert ref.required == ["code", "message"]

    code = ref.properties["code"]
    assert code.type == "integer"
    assert code.format == "int32"

    message = ref.properties["message"]
    assert message.type == "string"


def test_allOf_resolution(petstore_expanded_spec):
    """
    Tests that allOfs are resolved correctly
    """
    ref = petstore_expanded_spec.paths["/pets"].get.responses["200"].content["application/json"].schema_.get_type()

    assert type(ref) == ModelMetaclass
    assert typing.get_origin(ref.__fields__["__root__"].outer_type_) == list

    items = typing.get_args(ref.__fields__["__root__"].outer_type_)[0].__fields__

    assert sorted(map(lambda x: x.name, filter(lambda y: y.required == True, items.values()))) == sorted(["id", "name"])

    assert sorted(map(lambda x: x.name, items.values())) == ["id", "name", "tag"]

    assert items["id"].outer_type_ == int
    assert items["name"].outer_type_ == str
    assert items["tag"].outer_type_ == str


@dataclasses.dataclass
class _Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


@pytest.fixture(scope="session", params=[_Version(3, 0, 3), _Version(3, 1, 0)])
def openapi_version(request):
    return request.param


def test_schemaref(openapi_version):
    import aiopenapi3.v30.general
    import aiopenapi3.v31.general

    expected = {0: aiopenapi3.v30.general.Reference, 1: aiopenapi3.v31.general.Reference}[openapi_version.minor]

    SPEC = f"""openapi: {openapi_version}
info:
  title: API
  version: 1.0.0
paths:
  /pets:
    get:
      description: yes
      operationId: findPets
      responses:
        '200':
          description: pet response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Pet'
components:
  schemas:
    Pet:
      type: str
    """
    api = OpenAPI.loads("test.yaml", SPEC)
    print(api)

    assert api.paths["/pets"].get.responses["200"].content["application/json"].schema_.items.__class__ == expected
