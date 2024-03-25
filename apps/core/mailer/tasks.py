from uuid import UUID

from celery import shared_task
from django.utils import timezone

from apps.shared import DisperseModel
from apps.core.mailer.mail_control import SendMailController
from apps.core.mailer.mail_data import MailDataResolver


def get_config_template_user(tenant_id, company_id, user_id, system_code):
    mail_config_cls = DisperseModel(app_model='mailer.MailConfig').get_model()
    mail_template_cls = DisperseModel(app_model='mailer.MailTemplateSystem').get_model()
    if (
            mail_config_cls and hasattr(mail_config_cls, 'get_config')
            and mail_template_cls and hasattr(mail_template_cls, 'get_config')
    ):
        config_obj = mail_config_cls.get_config(tenant_id=tenant_id, company_id=company_id)
        template_obj = mail_template_cls.get_config(tenant_id=tenant_id, company_id=company_id, system_code=system_code)
        user_cls = DisperseModel(app_model='account.User').get_model()
        try:
            user_obj = user_cls.objects.get(pk=user_id)
        except user_cls.DoesNotExist:
            return 'USER_NOT_FOUND'

        return [config_obj, template_obj, user_obj]
    return 'MAIL_CONFIG_NOT_METHOD_GET'


@shared_task
def send_mail_welcome(tenant_id: UUID or str, company_id: UUID or str, user_id: UUID or str):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=user_id, system_code=1)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, template_obj, user_obj] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=3)
        if cls.is_active is True:
            if template_obj.contents:
                if user_obj.email:
                    state_send = cls.setup(
                        subject=template_obj.subject if template_obj.subject else 'Welcome to company',
                        from_email=cls.kwargs['from_email'],
                        mail_cc=cls.kwargs['cc_email'],
                        bcc=cls.kwargs['bcc_email'],
                        header={},
                        reply_to=cls.kwargs['reply_email'],
                    ).send(
                        mail_to=[user_obj.email],
                        template=template_obj.contents,
                        data=MailDataResolver.welcome(user_obj),
                    )
                    if state_send is True:
                        user_obj.is_mail_welcome += 1
                        user_obj.save(update_fields=['is_mail_welcome'])
                        return 'Success'
                    return 'SEND_FAILURE'
                return 'USER_EMAIL_IS_NOT_CORRECT'
            return 'TEMPLATE_HAS_NOT_CONTENTS_VALUE'
        return 'MAIL_CONFIG_DEACTIVATE'
    return obj_got


@shared_task
def send_mail_otp(  # pylint: disable=R0911,R1702
        tenant_id: UUID or str, company_id: UUID or str, user_id: UUID or str, otp_id: UUID or str, otp: str
):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=user_id, system_code=3)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, template_obj, user_obj] = obj_got

        otp_valid_cls = DisperseModel(app_model='account.ValidateUser').get_model()
        try:
            otp_obj = otp_valid_cls.objects.get(pk=otp_id)
        except otp_valid_cls.DoesNotExist:
            return 'OTP ID NOT FOUND: ' + str(otp_id)

        if config_obj and template_obj and user_obj and otp_obj:
            cls = SendMailController(mail_config=config_obj, timeout=3)
            if cls.is_active is True:
                if template_obj.contents:
                    if user_obj.email:
                        state_send = cls.setup(
                            subject=template_obj.subject if template_obj.subject else 'OTP validation',
                            from_email=cls.kwargs['from_email'],
                            mail_cc=cls.kwargs['cc_email'],
                            bcc=cls.kwargs['bcc_email'],
                            header={},
                            reply_to=cls.kwargs['reply_email'],
                        ).send(
                            mail_to=[user_obj.email],
                            template=template_obj.contents,
                            data=MailDataResolver.otp_verify(user_obj, otp),
                        )
                        if state_send is True:
                            otp_obj.is_sent = True
                            otp_obj.date_sent = timezone.now()
                            otp_obj.save(update_fields=['is_sent', 'date_sent'])
                            return 'Success'
                        return 'SEND_FAILURE'
                    return 'USER_EMAIL_IS_NOT_CORRECT'
                return 'TEMPLATE_HAS_NOT_CONTENTS_VALUE'
            return 'MAIL_CONFIG_DEACTIVATE'
    return obj_got


@shared_task
def send_mail_calendar():
    ...


@shared_task
def send_mail_feature():
    ...
