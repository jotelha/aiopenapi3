import pytest
from yaml import safe_load

from aiopenapi3 import OpenAPI

LOADED_FILES = {}
URLBASE = "/"


def _get_parsed_yaml(filename):
    """
    Returns a python dict that is a parsed yaml file from the tests/fixtures
    directory.

    :param filename: The filename to load.  Must exist in tests/fixtures and
                     include extension.
    :type filename: str
    """
    if filename not in LOADED_FILES:
        with open("tests/fixtures/" + filename) as f:
            raw = f.read()
        parsed = safe_load(raw)

        LOADED_FILES[filename] = parsed

    return LOADED_FILES[filename]


def _get_parsed_spec(filename):
    """
    Returns an OpenAPI object loaded from a file in the tests/fixtures directory

    :param filename: The filename to load.  Must exist in tests/fixtures and
                     include extension.
    :type filename: str
    """
    if "spec:" + filename not in LOADED_FILES:
        parsed = _get_parsed_yaml(filename)

        spec = OpenAPI(URLBASE, parsed)

        LOADED_FILES["spec:" + filename] = spec

    return LOADED_FILES["spec:" + filename]


@pytest.fixture
def petstore_expanded():
    """
    Provides the petstore-expanded.yaml spec
    """
    yield _get_parsed_yaml("petstore-expanded.yaml")


@pytest.fixture
def petstore_expanded_spec():
    """
    Provides an OpenAPI version of the petstore-expanded.yaml spec
    """
    yield _get_parsed_spec("petstore-expanded.yaml")


@pytest.fixture
def broken():
    """
    Provides the parsed yaml for a broken spec
    """
    yield _get_parsed_yaml("broken.yaml")


@pytest.fixture
def broken_reference():
    """
    Provides the parsed yaml for a spec with a broken reference
    """
    yield _get_parsed_yaml("broken-ref.yaml")


def has_bad_parameter_name():
    """
    Provides the parsed yaml for a spec with a bad parameter name
    """
    yield _get_parsed_yaml("bad-parameter-name.yaml")


@pytest.fixture
def dupe_op_id():
    """
    A spec with a duplicate operation ID
    """
    yield _get_parsed_yaml("dupe-operation-ids.yaml")


@pytest.fixture
def parameter_with_underscores():
    """
    A valid spec with underscores in a path parameter
    """
    yield _get_parsed_yaml("parameter-with-underscores.yaml")


@pytest.fixture
def obj_example_expanded():
    """
    Provides the obj-example.yaml spec
    """
    yield _get_parsed_yaml("obj-example.yaml")


@pytest.fixture
def float_validation_expanded():
    """
    Provides the float-validation.yaml spec
    """
    yield _get_parsed_yaml("float-validation.yaml")


@pytest.fixture
def has_bad_parameter_name():
    """
    Provides a spec with a bad parameter name
    """
    yield _get_parsed_yaml("bad-parameter-name.yaml")


@pytest.fixture
def with_links():
    """
    Provides a spec with links defined
    """
    yield _get_parsed_yaml("with-links.yaml")


@pytest.fixture
def with_broken_links():
    """
    Provides a spec with broken links defined
    """
    yield _get_parsed_yaml("with-broken-links.yaml")


@pytest.fixture
def with_securityparameters():
    """
    Provides a spec with security parameters
    """
    yield _get_parsed_yaml("with-securityparameters.yaml")


@pytest.fixture
def with_parameters():
    """
    Provides a spec with parameters
    """
    yield _get_parsed_yaml("with-parameters.yaml")


@pytest.fixture
def with_callback():
    """
    Provides a spec with callback
    """
    yield _get_parsed_yaml("callback-example.yaml")


@pytest.fixture
def with_swagger():
    yield _get_parsed_yaml("swagger-example.yaml")


@pytest.fixture
def with_allof_discriminator():
    yield _get_parsed_yaml("with-allof-discriminator.yaml")


@pytest.fixture
def with_enum():
    yield _get_parsed_yaml("with-enum.yaml")


@pytest.fixture
def with_anyOf_properties():
    yield _get_parsed_yaml("with-anyOf-properties.yaml")


@pytest.fixture
def with_schema_recursion():
    yield _get_parsed_yaml("with-schema-recursion.yaml")
