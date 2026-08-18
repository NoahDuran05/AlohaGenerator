import logging
import os
from typing import cast

import pytest

from aloha_email.email import Email
from aloha_email.email_envelope import EmailEnvelope
from aloha_email.email_utilities import send_email


logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)


REQUIRED_ENV_VARS = (
    "ALOHA_SENDGRID_API_KEY",
    "ALOHA_TEST_EMAIL_TO",
    "ALOHA_TEST_EMAIL_FROM",
    "ALOHA_TEST_EMAIL_REPLY_TO",
    "ALOHA_TEST_EMAIL_CC",
    "ALOHA_TEST_EMAIL_CC2",
    "ALOHA_TEST_EMAIL_BCC",
    "ALOHA_TEST_EMAIL_BCC2",
)


@pytest.mark.integration
@pytest.mark.skipif(
    any(not os.environ.get(var) for var in REQUIRED_ENV_VARS),
    reason=f"Requires environment variables: {', '.join(REQUIRED_ENV_VARS)}",
)
def test_send_email():
    """
    Live integration test.

    Sends a real email through SendGrid using addresses and credentials
    provided through environment variables.
    """

    data = {
        "subject": "Testing the astronauts have landed",
        "body": "Please read this carefully for errors",

        "to_addresses": [
            {
                "address": os.environ["ALOHA_TEST_EMAIL_TO"],
                "name": "Test Recipient",
            },
        ],

        "from_address": {
            "address": os.environ["ALOHA_TEST_EMAIL_FROM"],
            "name": "Aloha Support",
        },

        "reply_to_address": {
            "address": os.environ["ALOHA_TEST_EMAIL_REPLY_TO"],
            "name": "Test Reply To",
        },

        "cc_addresses": [
            {
                "address": os.environ["ALOHA_TEST_EMAIL_CC"],
                "name": "CC Recipient",
            },
            {
                "address": os.environ["ALOHA_TEST_EMAIL_CC2"],
            },
        ],

        "bcc_addresses": [
            {
                "address": os.environ["ALOHA_TEST_EMAIL_BCC"],
                "name": "BCC Recipient",
            },
            {
                "address": os.environ["ALOHA_TEST_EMAIL_BCC2"],
            },
        ],

        "enrollment_id": "test-enrollment-id",
        "correlation_id": "test-correlation-id",
    }

    # Validate the envelope.
    envelope = EmailEnvelope.model_validate(data)

    assert envelope is not None

    # Verify that the envelope contains enough information to send.
    envelope.ensure_sendable()

    # Build the Email object.
    email = Email()
    email.apply_envelope(envelope)

    email.subject = cast(str, data["subject"])
    email.body = cast(str, data["body"])
    email.enrollment_id = cast(str, data["enrollment_id"])
    email.correlation_id = cast(str, data["correlation_id"])

    # Verify Pydantic serialization/deserialization.
    email_json = email.model_dump_json()
    validated_email = Email.model_validate_json(email_json)

    assert validated_email.subject == data["subject"]
    assert validated_email.body == data["body"]
    assert validated_email.enrollment_id == data["enrollment_id"]
    assert validated_email.correlation_id == data["correlation_id"]

    # Send the real email.
    result = send_email(validated_email)

    assert result