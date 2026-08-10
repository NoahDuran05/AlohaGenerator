import logging
import os

import pytest

from .email import Email, EmailFromTemplate
from .template_utilities import get_templates, fill_template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    From,
    To,
    Cc,
    Bcc,
    CustomArg,
)


def send_email(email: Email):
    function = "(aloha) send_email"
    api_key = os.environ.get("ALOHA_SENDGRID_API_KEY")

    if not api_key:
        logging.error(
            "SendGrid API key (ALOHA_SENDGRID_API_KEY) not found in environment."
        )
        return False

    try:
        client = SendGridAPIClient(api_key)

        # Build the base message (no to_emails here)
        message = Mail(
            from_email=From(email.from_address.address, email.from_address.name),
            subject=email.subject,
            html_content=email.body,
        )

        if email.reply_to_address:
            try:
                message.reply_to = From(
                    email.reply_to_address.address,
                    email.reply_to_address.name,
                )
            except Exception as e:
                logging.exception(
                    f"{function}: Invalid reply_to_address: {e}"
                )
                # Still send the email; reply-to is optional.

        for addr in email.to_addresses:
            message.add_to(To(addr.address, addr.name))

        for addr in email.cc_addresses:
            message.add_cc(Cc(addr.address, addr.name))

        for addr in email.bcc_addresses:
            message.add_bcc(Bcc(addr.address, addr.name))

        if email.correlation_id:
            message.add_custom_arg(
                CustomArg("correlation_id", email.correlation_id)
            )

        if email.enrollment_id:
            message.add_custom_arg(
                CustomArg("enrollment_id", email.enrollment_id)
            )

        response = client.send(message)

        if 200 <= response.status_code < 300:
            logging.info(f"{function}: Email sent successfully.")
            return True

        logging.warning(
            f"{function}: Failed to send email. Status: {response.status_code}, "
            f"Body: "
            f"{response.body.decode() if hasattr(response.body, 'decode') else response.body}"
        )
        return False

    except Exception as ex:
        logging.error(
            f"{function}: Error sending email: {ex}",
            exc_info=True,
        )
        return False


def send_email_from_template(email_from_template: EmailFromTemplate):
    templates = get_templates(email_from_template.template_name)

    email = Email()
    email.subject = fill_template(
        templates["subject"],
        email_from_template.merge_fields,
    )
    email.body = fill_template(
        templates["body"],
        email_from_template.merge_fields,
    )
    email.from_address = email_from_template.from_address
    email.reply_to_address = email_from_template.reply_to_address
    email.to_addresses = email_from_template.to_addresses
    email.cc_addresses = email_from_template.cc_addresses
    email.bcc_addresses = email_from_template.bcc_addresses

    return send_email(email)


# ----------------------------------------------------------------------
# Hardcoded API URLs
# ----------------------------------------------------------------------
# No hardcoded API URLs are present in this file.
# SendGrid is accessed through SendGridAPIClient using the environment key.
#
# Any direct/hardcoded URL should remain commented out, for example:
#
# SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


# ----------------------------------------------------------------------
# Pytest Tests
# ----------------------------------------------------------------------
class DummyAddress:
    def __init__(self, address, name=None):
        self.address = address
        self.name = name


class DummyResponse:
    def __init__(self, status_code=202, body=b""):
        self.status_code = status_code
        self.body = body


@pytest.fixture
def basic_email():
    email = Email()
    email.from_address = DummyAddress(
        "sender@example.com",
        "Sender",
    )
    email.reply_to_address = None
    email.to_addresses = [
        DummyAddress("recipient@example.com", "Recipient")
    ]
    email.cc_addresses = []
    email.bcc_addresses = []
    email.subject = "Test subject"
    email.body = "<p>Test body</p>"
    email.correlation_id = ""
    email.enrollment_id = ""
    return email


def test_send_email_returns_false_when_api_key_missing(monkeypatch, basic_email):
    monkeypatch.delenv("ALOHA_SENDGRID_API_KEY", raising=False)

    result = send_email(basic_email)

    assert result is False


def test_send_email_success(monkeypatch, basic_email):
    monkeypatch.setenv("ALOHA_SENDGRID_API_KEY", "test-api-key")

    class MockClient:
        def __init__(self, api_key):
            assert api_key == "test-api-key"

        def send(self, message):
            return DummyResponse(status_code=202)

    monkeypatch.setattr(
        __name__ + ".SendGridAPIClient",
        MockClient,
    )

    result = send_email(basic_email)

    assert result is True


def test_send_email_failure_status(monkeypatch, basic_email):
    monkeypatch.setenv("ALOHA_SENDGRID_API_KEY", "test-api-key")

    class MockClient:
        def __init__(self, api_key):
            pass

        def send(self, message):
            return DummyResponse(
                status_code=400,
                body=b"Bad Request",
            )

    monkeypatch.setattr(
        __name__ + ".SendGridAPIClient",
        MockClient,
    )

    result = send_email(basic_email)

    assert result is False


def test_send_email_handles_sendgrid_exception(monkeypatch, basic_email):
    monkeypatch.setenv("ALOHA_SENDGRID_API_KEY", "test-api-key")

    class MockClient:
        def __init__(self, api_key):
            pass

        def send(self, message):
            raise RuntimeError("SendGrid unavailable")

    monkeypatch.setattr(
        __name__ + ".SendGridAPIClient",
        MockClient,
    )

    result = send_email(basic_email)

    assert result is False


def test_send_email_from_template(monkeypatch):
    template_email = EmailFromTemplate()
    template_email.template_name = "welcome"
    template_email.merge_fields = {
        "first_name": "Alice",
    }
    template_email.from_address = DummyAddress(
        "sender@example.com",
        "Sender",
    )
    template_email.reply_to_address = DummyAddress(
        "reply@example.com",
        "Reply",
    )
    template_email.to_addresses = [
        DummyAddress("recipient@example.com", "Recipient")
    ]
    template_email.cc_addresses = []
    template_email.bcc_addresses = []

    monkeypatch.setattr(
        __name__ + ".get_templates",
        lambda template_name: {
            "subject": "Welcome {{ first_name }}",
            "body": "<p>Hello {{ first_name }}</p>",
        },
    )

    def mock_fill_template(template, merge_fields):
        return template.replace(
            "{{ first_name }}",
            merge_fields["first_name"],
        )

    monkeypatch.setattr(
        __name__ + ".fill_template",
        mock_fill_template,
    )

    sent = {}

    def mock_send_email(email):
        sent["email"] = email
        return True

    monkeypatch.setattr(
        __name__ + ".send_email",
        mock_send_email,
    )

    result = send_email_from_template(template_email)

    assert result is True
    assert sent["email"].subject == "Welcome Alice"
    assert sent["email"].body == "<p>Hello Alice</p>"
    assert sent["email"].from_address.address == "sender@example.com"
    assert sent["email"].reply_to_address.address == "reply@example.com"
    assert sent["email"].to_addresses[0].address == "recipient@example.com"
