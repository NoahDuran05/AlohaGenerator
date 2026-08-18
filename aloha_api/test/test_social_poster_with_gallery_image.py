import os

import pytest

from aloha_api.enrollment_enums import AgenticAction, ImageSource
from aloha_api.enrollments import Enrollments
from aloha_api.social_poster_with_gallery_image import (
    SocialPosterWithGalleryImage,
)


REQUIRED_ENV_VARS = (
    "ALOHA_INTERNAL_API_KEY",
    "ALOHA_TEST_CLIENT_ID",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_social_poster_with_gallery_image():
    """
    Live integration test for SocialPosterWithGalleryImage.

    Retrieves an active social-media enrollment configured to use
    gallery images and executes the social poster for the configured
    test client.
    """

    api_key = os.environ["ALOHA_INTERNAL_API_KEY"]
    expected_client_id = os.environ["ALOHA_TEST_CLIENT_ID"]

    enrollments = Enrollments(api_key)
    social_poster = SocialPosterWithGalleryImage(api_key)

    assert enrollments is not None
    assert social_poster is not None

    # Retrieve active social enrollments using gallery images.
    social_enrollments = enrollments.get_active_enrollments(
        AgenticAction.PostSocialMedia,
        ImageSource.Gallery,
    )

    assert social_enrollments, "No active social gallery enrollments found"

    # Find the configured test enrollment rather than assuming it is first.
    enrollment = next(
        (
            enrollment
            for enrollment in social_enrollments
            if enrollment.get_client_id() == expected_client_id
        ),
        None,
    )

    assert enrollment is not None, (
        f"No social gallery enrollment found for test client "
        f"{expected_client_id}"
    )

    # Verify required enrollment configuration.
    scheduling_template_id = enrollment.get_scheduling_template_id()
    text_template_id = enrollment.get_text_template_id()

    assert scheduling_template_id is not None
    assert text_template_id is not None

    # Convert to the model expected by the social poster.
    social_enrollment = enrollment.to_social_enrollment()

    assert social_enrollment is not None

    # Execute the live social post.
    result = social_poster.execute_for_client(social_enrollment)

    # If execute_for_client intentionally returns None, remove this assertion.
    assert result is not None