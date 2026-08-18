import os

import pytest

from aloha_api.generator import Generator


REQUIRED_ENV_VARS = (
    "ALOHA_INTERNAL_API_KEY",
    "ALOHA_TEST_BOOLEAN_CLIENT_ID",
    "ALOHA_TEST_BOOLEAN_TEMPLATE_ID",
    "ALOHA_TEST_TEXT_CLIENT_ID",
    "ALOHA_TEST_TEXT_TEMPLATE_ID",
)


@pytest.fixture
def generator():
    """
    Create a Generator instance using the configured API key.
    """
    api_key = os.environ["ALOHA_INTERNAL_API_KEY"]

    instance = Generator.from_api_key(api_key)

    assert instance is not None

    return instance


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_generate_boolean(generator):
    """
    Integration test for boolean generation.
    """

    client_id = os.environ["ALOHA_TEST_BOOLEAN_CLIENT_ID"]
    template_id = os.environ["ALOHA_TEST_BOOLEAN_TEMPLATE_ID"]

    result = generator.generate_boolean(
        client_id,
        template_id,
    )

    assert result is not None
    assert isinstance(result, bool)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_generate_text(generator):
    """
    Integration test for text generation.
    """

    client_id = os.environ["ALOHA_TEST_TEXT_CLIENT_ID"]
    template_id = os.environ["ALOHA_TEST_TEXT_TEMPLATE_ID"]

    merge_fields = {
        "first_name": "Linda",
    }

    result = generator.generate_text(
        client_id,
        template_id,
        merge_fields,
    )

    assert result is not None
    assert isinstance(result, str)
    assert result.strip()