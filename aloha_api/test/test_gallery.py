import os

import pytest

from aloha_api.image_gallery import ImageGallery


REQUIRED_ENV_VARS = (
    "ALOHA_INTERNAL_API_KEY",
    "ALOHA_TEST_CLIENT_ID",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_get_random_image():
    """
    Integration test for ImageGallery.

    Creates an ImageGallery using the API key and retrieves a random
    image for the configured test client.
    """

    api_key = os.environ["ALOHA_INTERNAL_API_KEY"]
    client_id = os.environ["ALOHA_TEST_CLIENT_ID"]

    gallery = ImageGallery.from_api_key(api_key)

    assert gallery is not None

    image = gallery.get_random_image(client_id)

    assert image is not None