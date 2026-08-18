import os

import pytest

from aloha_blog.blog_post import BlogEntry, BlogMedia
from aloha_blog.wordpress_client import (
    WordPressClient,
    WordPressConnection,
)


REQUIRED_ENV_VARS = (
    "WP_WEBSITE",
    "WP_USERNAME",
    "WP_APP_PASSWORD",
    "WP_TEST_MEDIA_URL",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_create_wordpress_blog_post():
    """
    Live WordPress integration test.

    Uploads media and creates a WordPress blog post using credentials
    and URLs supplied through environment variables.
    """

    connection = WordPressConnection(
        website=os.environ["WP_WEBSITE"],
        username=os.environ["WP_USERNAME"],
        password=os.environ["WP_APP_PASSWORD"],
    )

    client = WordPressClient(connection)

    # Upload test media.
    blog_media = BlogMedia(
        url=os.environ["WP_TEST_MEDIA_URL"],
        title="Pytest media upload",
    )

    media = client.upload_media(blog_media)

    assert media is not None
    assert media.id is not None
    assert media.source_url is not None

    # Create the blog entry.
    blog_entry = BlogEntry(
        author="Test Author",
        title="Pytest WordPress Integration Test",
        content=(
            "<p>This is a test post created by the "
            "WordPress integration test.</p>"
        ),
        categories=["AI News"],
        status="Published",
    )

    wordpress_entry = client.to_wordpress_blog_entry(blog_entry)

    assert wordpress_entry is not None

    # Use uploaded media as the featured image.
    wordpress_entry.featured_media = media.id

    # Create the WordPress post.
    post = client.post_wp_entry(wordpress_entry)

    assert post is not None
    assert post.link is not None
    assert post.status is not None

    if post.title:
        assert post.title.raw is not None