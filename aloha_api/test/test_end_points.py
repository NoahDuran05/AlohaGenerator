import os

import pytest

from aloha_api.end_points import EndPoints


REQUIRED_ENV_VARS = (
    "ALOHA_INTERNAL_API_KEY",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_end_points_from_api_key():
    """
    Integration test for EndPoints.

    Creates EndPoints using the API key supplied through environment
    variables and verifies that the content endpoint is available.
    """

    api_key = os.environ["ALOHA_INTERNAL_API_KEY"]

    end_points = EndPoints.from_api_key(api_key)

    assert end_points is not None
    assert end_points.content is not None