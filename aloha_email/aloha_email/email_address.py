import logging
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError
from email_validator import validate_email, EmailNotValidError


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