import os

import pytest

from aloha_api.blog_poster import BlogPoster


REQUIRED_ENV_VARS = (
    "ALOHA_INTERNAL_API_KEY",
    "ALOHA_TEST_ENROLLMENT_ID",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_blog_poster_execute_for_enrollment():
    """
    Live integration test for BlogPoster.

    Executes a blog post request for an enrollment using credentials
    and identifiers supplied through environment variables.
    """

    api_key = os.environ["ALOHA_INTERNAL_API_KEY"]
    enrollment_id = os.environ["ALOHA_TEST_ENROLLMENT_ID"]

    blog_poster = BlogPoster(api_key)

    result = blog_poster.execute_for_enrollment(enrollment_id)

    assert result is not None
    assert result.url is not None
    assert result.status is not None
    assert result.title is not None