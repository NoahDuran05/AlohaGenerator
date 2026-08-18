import logging
import os
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
    function = '(aloha) send_email'
    api_key = os.environ.get("ALOHA_SENDGRID_API_KEY")

    if not api_key:
        logging.error("SendGrid API key (ALOHA_SENDGRID_API_KEY) not found in environment.")
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
                    email.reply_to_address.name
                )
            except Exception as e:
                logging.exception(f"{function}: Invalid reply_to_address: {e}")
                # Still send the email, reply-to is optional

        for addr in email.to_addresses:
            message.add_to(To(addr.address, addr.name))
        for addr in email.cc_addresses:
            message.add_cc(Cc(addr.address, addr.name))
        for addr in email.bcc_addresses:
            message.add_bcc(Bcc(addr.address, addr.name))

        if email.correlation_id:
            message.add_custom_arg(CustomArg("correlation_id", email.correlation_id))
        if email.enrollment_id:
            message.add_custom_arg(CustomArg("enrollment_id", email.enrollment_id))

        response = client.send(message)
        if 200 <= response.status_code < 300:
            logging.info(f"{function}: Email sent successfully.")
            return True
        else:
            logging.warning(
                f"{function}: Failed to send email. Status: {response.status_code}, "
                f"Body: {response.body.decode() if hasattr(response.body, 'decode') else response.body}"
            )
            return False

    except Exception as ex:
        logging.error(f"{function}:Error sending email: {ex}", exc_info=True)
        return False




def send_email_from_template(email_from_template: EmailFromTemplate):
    templates = get_templates(email_from_template.template_name)

    email = Email()
    email.subject = fill_template(templates['subject'], email_from_template.merge_fields)
    email.body = fill_template(templates['body'], email_from_template.merge_fields)
    email.from_address = email_from_template.from_address
    email.to_addresses = email_from_template.to_addresses
    email.cc_addresses = email_from_template.cc_addresses
    email.bcc_addresses = email_from_template.bcc_addresses
    return send_email(email)
