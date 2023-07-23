import email
import os.path

import base64
from email.message import MIMEPart

from django.template import Context
from django.template import Template
from django.utils.html import strip_tags
from django.conf import settings

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from apps.core.system.models import MailServerConfig
from apps.core.log.models import MailLog

__all__ = [
    'GmailController',
]


class MailLogController:
    def __init__(
            self,
            tenant_id,
            company_id,
            employee_id,
            mail_template,
            mail_context,
            mail_html,
            mail_text,
            mail_to,
            mail_cc,
            mail_bcc,
    ):
        self.obj = MailLog.objects.create(
            tenant_id=tenant_id,
            company_id=company_id,
            employee_id=employee_id,
            mail_template=mail_template,
            mail_context=mail_context,
            mail_html=mail_html,
            mail_text=mail_text,
            mail_to=mail_to,
            mail_cc=mail_cc,
            mail_bcc=mail_bcc,
            mail_receiver_data={
                'to': mail_to,
                'cc': mail_cc,
                'bcc': mail_bcc,
            }
        )

    def log_continue(self, **kwargs):
        key_list = []
        for key, value in kwargs.items():
            key_list.append(key)
            setattr(self.obj, key, value)
        self.obj.save(update_fields=key_list)
        return self.obj

    def log_finish(
            self,
            mail_id,
            mail_thread_id,
            mail_label_ids,
    ):
        if self.obj:
            self.obj.mail_id = mail_id
            self.obj.mail_thread_id = mail_thread_id
            self.obj.mail_label_ids = mail_label_ids
            self.obj.is_sent = True
            self.obj.save(update_fields=['mail_id', 'mail_thread_id', 'mail_label_ids', 'is_sent'])
            return self.obj
        raise ValueError('Must be run log_start before call finish')

    def log_full(
            self,
            mail_template,
            mail_context,
            mail_html,
            mail_text,
            mail_to,
            mail_cc,
            mail_bcc,
            mail_id,
            mail_thread_id,
            mail_label_ids,
    ):
        self.obj.mail_template = mail_template
        self.obj.mail_context = mail_context
        self.obj.mail_html = mail_html
        self.obj.mail_text = mail_text
        self.obj.mail_to = mail_to
        self.obj.mail_cc = mail_cc
        self.obj.mail_bcc = mail_bcc
        self.obj.mail_receiver_data = {
            'to': mail_to,
            'cc': mail_cc,
            'bcc': mail_bcc,
        }
        self.obj.mail_id = mail_id
        self.obj.mail_thread_id = mail_thread_id
        self.obj.mail_label_ids = mail_label_ids
        self.obj.is_sent = True
        self.obj.save()
        return self.obj


class GmailController:
    TEMPLATE_DEMO = """
        <table style="width: 100%; max-width: 600px; margin: 0 auto; padding: 20px;">
            <tr>
                <td>
                    <img src="{{avatar_url}}" alt="avatar">
                </td>
            </tr>
            <tr>
                <td>
                    <h1>Hello,</h1>
                    <p>This is a sample email template.</p>
                    <p>You can customize it to suit your needs.</p>
                    <p>Regards,</p>
                    <p>Your Name</p>
                </td>
            </tr>
        </table>
    """
    CONTEXT_DEMO = {
        'avatar_url': 'https://cloud.mtsolution.com.vn/api/p/f/avatar'
                      '/120c4b6b81d158406decd2b0334991011d4c702f5e1f8fa192d419c9846e74ac',
    }
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.send',
    ]

    @staticmethod
    def get_raw_content(msg: MIMEPart) -> base64:
        return base64.urlsafe_b64encode(msg.as_bytes()).decode()

    @staticmethod
    def generate_template(
            template, context
    ) -> (str, str):
        template_render = Template(
            template
        ).render(
            Context(
                context
            )
        )
        return template_render, strip_tags(template_render)

    @classmethod
    def generate_message(
            cls,
            subject: str,
            to: list[str],
            template: str,
            context: dict[str, str] = dict,
            cc: list[str] = list,
            bcc: list[str] = list,
    ) -> (MIMEPart, str):
        msg = email.message.EmailMessage()
        msg["Subject"] = subject
        msg["To"] = to
        msg["Cc"] = cc if cc else []
        msg["Bcc"] = bcc if bcc else []
        msg.set_type("text/html")

        html, text = cls.generate_template(
            template=template,
            context=context if context else {}
        )
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")

        return msg, text

    @classmethod
    def authorized_user_info(cls):
        obj = MailServerConfig.objects.get(pk=settings.MAIL_CONFIG_OBJ_PK)
        creds = Credentials.from_authorized_user_info(obj.tokens, cls.SCOPES)
        return creds

    @classmethod
    def authorized_file(cls):
        token_path = os.path.join(settings.BASE_DIR, 'gmail', 'token._offline.json')
        cred_path = os.path.join(settings.BASE_DIR, 'gmail', 'credentials.json')

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, cls.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_path, cls.SCOPES,
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def __init__(
            self,
            subject: str,
            to: list[str],
            template: str,
            context: dict[str] = None,
            cc: list[str] = None,
            bcc: list[str] = None,
            thread_id: str = None,
            **kwargs,
    ):
        self.thread_id = thread_id
        self.creds = self.authorized_user_info()
        if not self.creds:
            raise ValueError('Credential gmail setup is failure!')

        self.subject: str = subject
        self.template: str = template
        self.to: list[str] = to or []
        self.context: dict[str] = context
        self.cc: list[str] = cc or []
        self.bcc: list[str] = bcc or []
        self.service: build = build('gmail', 'v1', credentials=self.creds)
        self.msg, self.msg_text = self.generate_message(
            subject=self.subject,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            template=self.template,
            context=context,
        )
        self.msg_raw: base64 = self.get_raw_content(msg=self.msg)
        self.log_obj: MailLogController = MailLogController(
            tenant_id=kwargs.get('tenant_id', None),
            company_id=kwargs.get('company_id', None),
            employee_id=kwargs.get('employee_id', None),
            mail_template=self.template,
            mail_context=self.context,
            mail_html=self.msg,
            mail_text=self.msg_text,
            mail_to=self.to,
            mail_cc=self.cc,
            mail_bcc=self.bcc,
        )

    def create_draft(self):
        try:
            draft = self.service.users().drafts().create(userId="me", body={'raw': self.msg_raw}).execute()
            self.log_obj.log_finish(
                mail_id=draft['id'],
                mail_thread_id=draft['threadId'],
                mail_label_ids=draft['labelIds'],
            )
        except HttpError as error:
            print(F'An error occurred: {error}')
            draft = None

        return draft

    def send(self):
        try:
            send_message = self.service.users().messages().send(
                userId="me", body={
                    'raw': self.msg_raw,
                    'threadId': self.thread_id,
                }
            ).execute()
            self.log_obj.log_finish(
                mail_id=send_message['id'],
                mail_thread_id=send_message['threadId'],
                mail_label_ids=send_message['labelIds'],
            )
        except HttpError as error:
            print(f'An error occurred: {error}')
            send_message = None
        return send_message
