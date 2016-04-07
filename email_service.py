from sendgrid import SendGridClient
from sendgrid import Mail
import conf


class EmailService(object):
    """
    EmailService singleton, uses SendGrid to send emails.
    Up to 12k emails free monthly.
    """
    _instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                EmailService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def send_email(self,
                   from_email,
                   to_emails,
                   subject,
                   body):
        # make a secure connection to SendGrid
        sg = SendGridClient(conf.sendgrid_user, conf.sendgrid_pass, secure=True)

        # make a message object
        message = Mail()
        message.set_subject(subject)
        message.set_text(body)
        message.set_from(from_email)
        # add a recipient
        for to in to_emails:
            message.add_to(to)
        sg.send(message)