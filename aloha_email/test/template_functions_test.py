import pytest

from aloha_email.template_utilities import (
    read_email_template_file_from_azure,
    get_templates,
)


def test_read_email_template_file_from_azure():
    body = read_email_template_file_from_azure(
        "social/token-authorization-body.j2"
    )

    assert body is not None
    assert isinstance(body, str)
    assert body.strip()


def test_get_templates():
    templates = get_templates(
        "social/token-authorization"
    )

    assert templates is not None