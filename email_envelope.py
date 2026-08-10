from typing import Optional, List
import logging

import pytest
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .email_address import EmailAddress


logger = logging.getLogger(__name__)


class EmailEnvelope(BaseModel):

    model_config = ConfigDict(
        extra="ignore"
    )

    # ------------------------------------------------------------------
    # Address fields
    # ------------------------------------------------------------------
    from_address: Optional[EmailAddress] = None
    reply_to_address: Optional[EmailAddress] = None
    to_addresses: List[EmailAddress] = []
    cc_addresses: List[EmailAddress] = []
    bcc_addresses: List[EmailAddress] = []

    # ------------------------------------------------------------------
    # Deduplication logic
    # ------------------------------------------------------------------
    @staticmethod
    def dedupe_addresses(address_list: List[EmailAddress]) -> List[EmailAddress]:
        result = {}
        for addr in address_list:
            key = addr.address.strip().lower()
            if key not in result or (addr.name and not result[key].name):
                result[key] = addr
        return list(result.values())

    # ------------------------------------------------------------------
    # Field-level cleanup
    # ------------------------------------------------------------------
    @field_validator("to_addresses", "cc_addresses", "bcc_addresses", mode="before")
    @classmethod
    def filter_invalid_entries(cls, value):
        """
        Remove entries with invalid email addresses instead of failing.
        Matches legacy from_json_dict behavior.
        """
        if not value:
            return []

        cleaned = []

        for entry in value:
            if isinstance(entry, dict):
                addr = entry.get("address")
                name = entry.get("name")

                if not addr:
                    continue

                try:
                    EmailAddress(address=addr, name=name)
                    cleaned.append(entry)
                except Exception as e:
                    logger.warning(
                        f"(aloha) EmailEnvelope: dropping invalid email address '{addr}': {e}"
                    )

            else:
                cleaned.append(entry)

        return cleaned

    # ------------------------------------------------------------------
    # Model-level normalization (NOT required-field enforcement)
    # ------------------------------------------------------------------
    @model_validator(mode="after")
    def normalize_envelope(self):
        self.to_addresses = self.dedupe_addresses(self.to_addresses)
        self.cc_addresses = self.dedupe_addresses(self.cc_addresses)
        self.bcc_addresses = self.dedupe_addresses(self.bcc_addresses)
        return self

    def ensure_sendable(self) -> None:
        """
        Raises ValueError if the envelope cannot be sent.
        Use at send boundaries.
        """
        if not self.from_address or not self.from_address.address:
            raise ValueError("Email is missing from_address")

        if not self.to_addresses:
            raise ValueError("Email must have at least one To address")


# ----------------------------------------------------------------------
# Hardcoded API URLs
# ----------------------------------------------------------------------
# No hardcoded API URLs are present in this file.
# Any hardcoded API URLs should be commented out.
#
# EMAIL_API_URL = "https://api.example.com/email"


# ----------------------------------------------------------------------
# Pytest Tests
# ----------------------------------------------------------------------
def test_envelope_defaults():
    envelope = EmailEnvelope()

    assert envelope.from_address is None
    assert envelope.reply_to_address is None
    assert envelope.to_addresses == []
    assert envelope.cc_addresses == []
    assert envelope.bcc_addresses == []


def test_dedupe_addresses_case_insensitive():
    addresses = [
        EmailAddress(address="Test@gmail.com"),
        EmailAddress(address="test@gmail.com"),
    ]

    result = EmailEnvelope.dedupe_addresses(addresses)

    assert len(result) == 1
    assert result[0].address == "Test@gmail.com"


def test_dedupe_prefers_entry_with_name():
    addresses = [
        EmailAddress(address="test@gmail.com"),
        EmailAddress(address="TEST@gmail.com", name="Test User"),
    ]

    result = EmailEnvelope.dedupe_addresses(addresses)

    assert len(result) == 1
    assert result[0].name == "Test User"


def test_invalid_address_is_dropped():
    envelope = EmailEnvelope(
        to_addresses=[
            {"address": "valid@gmail.com", "name": "Valid User"},
            {"address": "not-an-email", "name": "Invalid User"},
        ]
    )

    assert len(envelope.to_addresses) == 1
    assert envelope.to_addresses[0].address == "valid@gmail.com"


def test_entry_without_address_is_dropped():
    envelope = EmailEnvelope(
        to_addresses=[
            {"name": "Missing Address"},
        ]
    )

    assert envelope.to_addresses == []


def test_ensure_sendable_requires_from_address():
    envelope = EmailEnvelope(
        to_addresses=[
            EmailAddress(address="recipient@gmail.com")
        ]
    )

    with pytest.raises(ValueError, match="Email is missing from_address"):
        envelope.ensure_sendable()


def test_ensure_sendable_requires_to_address():
    envelope = EmailEnvelope(
        from_address=EmailAddress(address="sender@gmail.com")
    )

    with pytest.raises(ValueError, match="Email must have at least one To address"):
        envelope.ensure_sendable()


def test_ensure_sendable_succeeds():
    envelope = EmailEnvelope(
        from_address=EmailAddress(address="sender@gmail.com"),
        to_addresses=[
            EmailAddress(address="recipient@gmail.com")
        ],
    )

    envelope.ensure_sendable()
