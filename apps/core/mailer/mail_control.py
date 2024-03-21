
__all__ = ['SendMailController']

import json

from django.core.mail import get_connection, EmailMultiAlternatives
from apps.core.mailer.handle_html import HTMLController
# from django.core.mail.backends.smtp import EmailBackend


class SendMailController:  # pylint: disable=R0902
    subject: str
    from_email: str
    mail_cc: list[str]
    bcc: list[str]
    header: dict[str, any]
    reply_to: str

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.connection = get_connection(**kwargs)

    def setup(self, **kwargs):
        self.subject = kwargs.get('subject', '')
        self.from_email = kwargs.get('from_email', '')
        self.mail_cc = kwargs.get('cc', [])
        self.bcc = kwargs.get('bcc', [])
        self.header = kwargs.get('headers', {})
        self.reply_to = kwargs.get('reply_to', '')

    def send(self, mail_to, template, data):
        # setup email
        msg = EmailMultiAlternatives(
            subject=self.subject,
            body=json.dumps(data),
            from_email=self.from_email,
            to=mail_to,
            cc=self.mail_cc,
            bcc=self.bcc,
            headers=self.header,
            reply_to=self.reply_to,
            connection=self.connection,
        )
        html_content = HTMLController(html_str=template).handle_params(data=data)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
