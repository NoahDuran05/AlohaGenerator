import os

import pytest

from aloha_api.enrollments import (
    Enrollments,
    AgenticAction,
    ImageSource,
)


REQUIRED_ENV_VARS = (
    "ALOHA_INTERNAL_API_KEY",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_get_active_enrollments():
    """
    Integration test for Enrollments.

    Verifies that active enrollments can be retrieved for social media
    and blog agentic actions.
    """

    api_key = os.environ["ALOHA_INTERNAL_API_KEY"]

    enrollments = Enrollments(api_key)

    assert enrollments is not None

    # Social media enrollments using generated images.
    social_generated_image_enrollments = enrollments.get_active_enrollments(
        AgenticAction.PostSocialMedia,
        ImageSource.Generate,
    )

    assert social_generated_image_enrollments is not None

    for enrollment in social_generated_image_enrollments:
        assert enrollment.get_client_id() is not None
        assert enrollment.get_text_template_id() is not None

    # Social media enrollments using gallery images.
    social_gallery_image_enrollments = enrollments.get_active_enrollments(
        AgenticAction.PostSocialMedia,
        ImageSource.Gallery,
    )

    assert social_gallery_image_enrollments is not None

    for enrollment in social_gallery_image_enrollments:
        assert enrollment.get_client_id() is not None
        assert enrollment.get_text_template_id() is not None

    # Blog enrollments.
    blog_enrollments = enrollments.get_active_enrollments(
        AgenticAction.PostBlogEntry,
    )

    assert blog_enrollments is not None

    for enrollment in blog_enrollments:
        assert enrollment.get_client_id() is not None
        assert enrollment.get_enrollment_id() is not None