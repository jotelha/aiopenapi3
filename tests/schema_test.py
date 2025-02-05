import sys
from unittest.mock import MagicMock, patch

if sys.version_info >= (3, 9):
    from pathlib import Path
else:
    from pathlib3x import Path

import httpx
import pytest
from pydantic import ValidationError

import aiopenapi3
from aiopenapi3 import OpenAPI


def test_invalid_response(httpx_mock, petstore_expanded):
    httpx_mock.add_response(headers={"Content-Type": "application/json"}, json={"foo": 1})
    api = OpenAPI("test.yaml", petstore_expanded, session_factory=httpx.Client)

    with pytest.raises(ValidationError, match="2 validation errors for Pet") as r:
        p = api._.find_pet_by_id(data={}, parameters={"id": 1})


def test_schema_without_properties(httpx_mock):
    """
    Tests that a response model is generated, and responses parsed correctly, for
    response schemas without properties
    """
    api = OpenAPI.load_file(
        "/test.yaml",
        Path("with-no-properties.yaml"),
        loader=aiopenapi3.FileSystemLoader(Path("tests/fixtures")),
        session_factory=httpx.Client,
    )
    httpx_mock.add_response(
        headers={"Content-Type": "application/json"},
        json={
            "example": "it worked",
            "no_properties": {},
        },
    )

    result = api._.noProps()
    assert result.example == "it worked"

    # the schema without properties did get its own named type defined
    assert type(result.no_properties).__name__ == "has_no_properties"
    # and it has no fields
    assert len(result.no_properties.__fields__) == 0


def test_schema_anyOf_properties(with_anyOf_properties):
    api = OpenAPI("/", with_anyOf_properties)
    s = api.components.schemas["AB"]
    t = s.get_type()

    # the semantics …
    A = next(filter(lambda x: x.type_.__name__ == "A", t.__fields__["__root__"].sub_fields))
    kwargs = {"ofA": 1, "id": 2}
    obj = A.type_(**kwargs)
    assert obj.dict() == kwargs
    ab = t(__root__=obj)
    assert ab


def test_schema_recursion(with_schema_recursion):
    with pytest.raises(RecursionError):
        api = OpenAPI("/", with_schema_recursion)


#    s = api.components.schemas["A"]
#    t = s.get_type()
