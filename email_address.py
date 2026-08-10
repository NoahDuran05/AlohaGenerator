import logging
from typing import Optional

import pytest
from pydantic import BaseModel, field_validator, ValidationError
from email_validator import validate_email, EmailNotValidError


logger = logging.getLogger(__name__)


class EmailAddress(BaseModel):
    address: str
    name: Optional[str] = None

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        # Validates and raises exception on error (matches original behavior)
        try:
            validate_email(v, check_deliverability=True)
            return v
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {e}")


# ----------------------------------------------------------------------
# Hardcoded API URLs
# ----------------------------------------------------------------------
# No hardcoded API URLs are present in this file.
# Any hardcoded API URLs should be commented out.
#
# EMAIL_VALIDATION_API_URL = "https://api.example.com/validate-email"


# ----------------------------------------------------------------------
# Pytest Tests
# ----------------------------------------------------------------------
def test_email_address_with_valid_email():
    email = EmailAddress(address="test@gmail.com")

    assert email.address == "test@gmail.com"
    assert email.name is None


def test_email_address_with_name():
    email = EmailAddress(
        address="test@gmail.com",
        name="Test User",
    )

    assert email.address == "test@gmail.com"
    assert email.name == "Test User"


def test_email_address_with_invalid_email():
    with pytest.raises(ValidationError):
        EmailAddress(address="not-an-email")
