from typing import Optional, Dict, List
import logging
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from .email_address import EmailAddress


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
                    # Attempt to validate address here
                    EmailAddress(address=addr, name=name)
                    cleaned.append(entry)
                except Exception as e:
                    logging.warning(
                        f"(aloha) EmailEnvelope: dropping invalid email address '{addr}': {e}"
                    )

            else:
                # Already an EmailAddress instance
                cleaned.append(entry)

        return cleaned

    # ------------------------------------------------------------------
    # Model-level normalization (NOT required-field enforcement)
    # ------------------------------------------------------------------
    @model_validator(mode="after")
    def normalize_envelope(self):
        # Deduplicate address lists
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

