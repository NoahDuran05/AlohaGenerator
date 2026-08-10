import logging

import pytest

from .email_envelope import EmailEnvelope


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Email
# ----------------------------------------------------------------------
class Email(EmailEnvelope):
    subject: str = ""
    body: str = ""
    enrollment_id: str = ""
    correlation_id: str = ""

    def apply_envelope(self, envelope: "EmailEnvelope"):
        self.from_address = envelope.from_address
        self.reply_to_address = envelope.reply_to_address
        self.to_addresses = envelope.to_addresses
        self.cc_addresses = envelope.cc_addresses
        self.bcc_addresses = envelope.bcc_addresses


# ----------------------------------------------------------------------
# EmailFromTemplate
# ----------------------------------------------------------------------
class EmailFromTemplate(EmailEnvelope):
    template_name: str = ""
    merge_fields: dict = {}


# ----------------------------------------------------------------------
# Hardcoded API URLs
# ----------------------------------------------------------------------
# Comment out any hardcoded API URLs.
#
# EMAIL_API_URL = "https://api.example.com/email"
# TEMPLATE_API_URL = "https://api.example.com/templates"


# ----------------------------------------------------------------------
# Pytest Tests
# ----------------------------------------------------------------------
@pytest.fixture
def envelope():
    envelope = EmailEnvelope()
    envelope.from_address = "sender@example.com"
    envelope.reply_to_address = "reply@example.com"
    envelope.to_addresses = ["recipient@example.com"]
    envelope.cc_addresses = ["cc@example.com"]
    envelope.bcc_addresses = ["bcc@example.com"]
    return envelope


def test_email_defaults():
    email = Email()

    assert email.subject == ""
    assert email.body == ""
    assert email.enrollment_id == ""
    assert email.correlation_id == ""


def test_apply_envelope(envelope):
    email = Email()

    email.apply_envelope(envelope)

    assert email.from_address == envelope.from_address
    assert email.reply_to_address == envelope.reply_to_address
    assert email.to_addresses == envelope.to_addresses
    assert email.cc_addresses == envelope.cc_addresses
    assert email.bcc_addresses == envelope.bcc_addresses


def test_email_from_template_defaults():
    email = EmailFromTemplate()

    assert email.template_name == ""
    assert email.merge_fields == {}
