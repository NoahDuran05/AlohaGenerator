import logging
from .email_envelope import EmailEnvelope

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
# EmailFromTemplate (Extends EmailEnvelope)
# ----------------------------------------------------------------------
class EmailFromTemplate(EmailEnvelope):
    template_name: str = ""
    merge_fields: dict = {}


