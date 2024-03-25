__all__ = ['SendMailController']

import json

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.utils import timezone
from django.core.mail import send_mail

from apps.core.mailer.handle_html import HTMLController

from apps.shared import FORMATTING


class SendMailController:  # pylint: disable=R0902
    is_active: bool
    subject: str
    from_email: str
    mail_cc: list[str]
    bcc: list[str]
    header: dict[str, any]
    reply_to: str
    data: dict
    template: str

    def __init__(self, mail_config=None, is_active=True, **kwargs):
        """

        Args:
            mail_config: MailConfig object
            is_active: unavailable when mail_config has value
            **kwargs:
        """
        if mail_config and mail_config.use_our_server is False:
            self.is_active = mail_config.is_active
            real_data = mail_config.get_real_data()
            ctx = {
                'host': real_data['host'],
                'port': real_data['port'],
                'username': real_data['username'],
                'password': real_data['password'],
                'use_tls': mail_config.use_tls,
                'use_ssl': mail_config.use_ssl,
                'ssl_keyfile': mail_config.get_ssl_key(),
                'ssl_certfile': mail_config.get_ssl_cert(),
                'from_email': real_data['from_email'],
                'reply_email': real_data['reply_email'],
                'cc_email': real_data['cc_email'],
                'bcc_email': real_data['bcc_email'],
            }
        else:
            self.is_active = is_active
            ctx = {
                'host': settings.EMAIL_SERVER_DEFAULT_HOST,
                'port': settings.EMAIL_SERVER_DEFAULT_PORT,
                'username': settings.EMAIL_SERVER_DEFAULT_USERNAME,
                'password': settings.EMAIL_SERVER_DEFAULT_PASSWORD,
                'use_tls': settings.EMAIL_SERVER_DEFAULT_USE_TLS,
                'use_ssl': settings.EMAIL_SERVER_DEFAULT_USE_SSL,
                'ssl_keyfile': settings.EMAIL_SERVER_DEFAULT_SSL_KEY,
                'ssl_certfile': settings.EMAIL_SERVER_DEFAULT_SSL_CERT,
                'from_email': settings.EMAIL_SERVER_DEFAULT_USERNAME,
                'reply_email': settings.EMAIL_SERVER_DEFAULT_REPLY,
                'cc_email': settings.EMAIL_SERVER_DEFAULT_CC,
                'bcc_email': settings.EMAIL_SERVER_DEFAULT_BCC,
            }
        self.kwargs = {
            'timeout': 1,
            **ctx,
            **kwargs,
        }

    @property
    def connection(self) -> EmailBackend:
        return get_connection(**self.kwargs)

    @classmethod
    def data_resolve(cls, data: dict):
        tz_now = timezone.now()
        return {
            **data,
            '_current_date': FORMATTING.parse_datetime(tz_now, '%d/%m/%Y'),
            '_current_date_solemn': FORMATTING.parse_date(tz_now, 'ngày %d tháng %m năm %Y'),
            '_current_date_time': FORMATTING.parse_datetime(tz_now, '%d/%m/%Y %H:%M:%S')
        }

    def setup(self, **kwargs):
        self.subject = kwargs.get('subject', '')
        self.from_email = kwargs.get('from_email', self.kwargs['from_email'])
        self.mail_cc = kwargs.get('cc', self.kwargs['cc_email'])
        self.bcc = kwargs.get('bcc', self.kwargs['bcc_email'])
        self.header = kwargs.get('headers', {})
        self.reply_to = kwargs.get('reply_to', self.kwargs['reply_email'])

        if not self.from_email:
            self.from_email = self.kwargs['username']
        return self

    def send(self, mail_to, template, data):
        try:
            with self.connection as connection:
                data = self.data_resolve(data=data)
                html_content = HTMLController(html_str=template, is_unescape=True).handle_params(data=data).to_string()
                send_mail(
                    subject=self.subject,
                    message=json.dumps(data),
                    from_email=self.from_email,
                    recipient_list=mail_to if isinstance(mail_to, list) else [mail_to],
                    connection=connection,
                    html_message=HTMLController.unescape(html_content),
                )
                return True
        except Exception as err:
            print('[SendMailController][send]', str(err))
            return f'Errors: {str(err)}'
