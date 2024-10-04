from uuid import UUID

from celery import shared_task
from django.utils import timezone

from apps.shared import DisperseModel
from apps.core.mailer.mail_control import SendMailController
from apps.core.mailer.mail_data import MailDataResolver
from apps.core.mailer.utils import MailLogController


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
        if user_id:
            try:
                user_obj = user_cls.objects.get(pk=user_id)
            except user_cls.DoesNotExist:
                return 'USER_NOT_FOUND'
        else:
            user_obj = None

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
                    subject = template_obj.subject if template_obj.subject else 'Welcome to company'

                    log_cls = MailLogController(
                        tenant_id=tenant_id, company_id=company_id,
                        system_code=1,  # WELCOME
                        doc_id=user_id, subject=subject,
                    )
                    log_cls.create()
                    log_cls.update(
                        address_sender=cls.from_email,
                    )
                    log_cls.update_employee_to(employee_to=[], address_to_init=[user_obj.email])
                    log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
                    log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
                    log_cls.update_log_data(host=cls.host, port=cls.port)

                    try:
                        state_send = cls.setup(
                            subject=subject,
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
                    except Exception as err:
                        state_send = False
                        log_cls.update(errors_data=str(err))

                    if state_send is True:
                        log_cls.update(status_code=1, status_remark=state_send)  # sent
                        log_cls.save()
                        user_obj.is_mail_welcome += 1
                        user_obj.save(update_fields=['is_mail_welcome'])
                        return 'Success'
                    log_cls.update(status_code=2, status_remark=state_send)  # error
                    log_cls.save()
                    return 'SEND_FAILURE'
                return 'USER_EMAIL_IS_NOT_CORRECT'
            return 'TEMPLATE_HAS_NOT_CONTENTS_VALUE'
        return 'MAIL_CONFIG_DEACTIVATE'
    return obj_got


@shared_task
def send_mail_otp(  # pylint: disable=R0911,R1702,R0914
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

                        subject = template_obj.subject if template_obj.subject else 'OTP validation'

                        log_cls = MailLogController(
                            tenant_id=tenant_id, company_id=company_id,
                            system_code=3,  # OTP Valid
                            doc_id=user_id, subject=subject
                        )
                        log_cls.create()
                        log_cls.update(
                            address_sender=cls.from_email,
                        )
                        log_cls.update_employee_to(employee_to=[], address_to_init=[user_obj.email])
                        log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
                        log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
                        log_cls.update_log_data(host=cls.host, port=cls.port)

                        try:
                            state_send = cls.setup(
                                subject=subject,
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
                        except Exception as err:
                            state_send = False
                            log_cls.update(errors_data=str(err))

                        if state_send is True:
                            log_cls.update(status_code=1, status_remark=state_send)  # sent
                            log_cls.save()
                            otp_obj.is_sent = True
                            otp_obj.date_sent = timezone.now()
                            otp_obj.save(update_fields=['is_sent', 'date_sent'])
                            return 'Success'
                        log_cls.update(status_code=2, status_remark=state_send)  # error
                        log_cls.save()
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


@shared_task
def send_mail_form(tenant_id, company_id, subject, to_main, contents):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=None, system_code=1)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, _template_obj, _user_obj] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=3)
        if cls.is_active is True:
            log_cls = MailLogController(
                tenant_id=tenant_id, company_id=company_id,
                system_code=4,  # FORM
                subject=subject
            )
            log_cls.create()
            log_cls.update(
                address_sender=cls.from_email,
            )
            log_cls.update_employee_to(employee_to=[], address_to_init=to_main)
            log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
            log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
            log_cls.update_log_data(host=cls.host, port=cls.port)

            try:
                state_send = cls.setup(
                    subject=subject,
                    from_email=cls.kwargs['from_email'],
                    mail_cc=cls.kwargs['cc_email'],
                    bcc=cls.kwargs['bcc_email'],
                    header={},
                    reply_to=cls.kwargs['reply_email'],
                ).send(
                    mail_to=to_main,
                    template=contents,
                    data={},
                )
            except Exception as err:
                state_send = False
                log_cls.update(errors_data=str(err))

            if state_send is True:
                log_cls.update(status_code=1, status_remark=state_send)  # sent
                log_cls.save()
                return 'Success'
            log_cls.update(status_code=2, status_remark=state_send)  # error
            log_cls.save()
            return 'SEND_FAILURE'
        return 'MAIL_CONFIG_DEACTIVATE'
    return obj_got


@shared_task
def send_mail_form_otp(subject, to_mail, contents, timeout=10, tenant_id=None, company_id=None, form_id=None):
    cls = SendMailController(mail_config=None, timeout=timeout)
    if cls.is_active is True:
        log_cls = MailLogController(
            tenant_id=tenant_id, company_id=company_id,
            doc_id=form_id,
            system_code=5,  # FORM OTP VALID
            subject=subject
        )
        log_cls.create()
        log_cls.update(
            address_sender=cls.from_email,
        )
        log_cls.update_employee_to(employee_to=[], address_to_init=to_mail)
        log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
        log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
        log_cls.update_log_data(host=cls.host, port=cls.port)

        try:
            cls.setup(
                subject=subject,
                from_email=cls.kwargs['from_email'],
                mail_cc=cls.kwargs['cc_email'],
                bcc=cls.kwargs['bcc_email'],
                header={},
                reply_to=cls.kwargs['reply_email'],
            )
            state_send = cls.send(
                mail_to=to_mail,
                template=contents,
                data={},
            )
        except Exception as err:
            state_send = False
            log_cls.update(errors_data=str(err))
        if state_send is True:
            log_cls.update(status_code=1, status_remark=state_send)  # sent
            log_cls.save()
            return True
        log_cls.update(status_code=2, status_remark=state_send)  # error
        log_cls.save()
        return 'SEND_FAILURE'
    return 'MAIL_CONFIG_DEACTIVATE'


@shared_task
def send_mail_workflow(
        tenant_id: UUID or str,
        company_id: UUID or str,
        user_id: UUID or str,
        employee_obj,
        runtime_obj,
        workflow_type,
):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=user_id, system_code=4)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, template_obj, user_obj] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=3)
        if cls.is_active is True and template_obj and user_obj and employee_obj:
            if template_obj.contents and user_obj.email and employee_obj.email:
                subject = template_obj.subject if template_obj.subject else 'Workflow'

                log_cls = MailLogController(
                    tenant_id=tenant_id, company_id=company_id,
                    system_code=4,  # WORKFLOW
                    doc_id=user_id, subject=subject,
                )
                if log_cls.create():
                    log_cls.update(
                        address_sender=cls.from_email,
                    )
                    log_cls.update_employee_to(employee_to=[], address_to_init=[employee_obj.email])
                    log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
                    log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
                    log_cls.update_log_data(host=cls.host, port=cls.port)

                    try:
                        state_send = cls.setup(
                            subject=subject,
                            from_email=cls.kwargs['from_email'],
                            mail_cc=cls.kwargs['cc_email'],
                            bcc=cls.kwargs['bcc_email'],
                            header={},
                            reply_to=cls.kwargs['reply_email'],
                        ).send(
                            mail_to=[employee_obj.email],
                            template=template_obj.contents,
                            data=MailDataResolver.workflow(runtime_obj=runtime_obj, workflow_type=workflow_type),
                        )
                    except Exception as err:
                        state_send = False
                        log_cls.update(errors_data=str(err))

                    if state_send is True:
                        log_cls.update(status_code=1, status_remark=state_send)  # sent
                        log_cls.save()
                        return 'Success'
                    log_cls.update(status_code=2, status_remark=state_send)  # error
                    log_cls.save()
                return 'SEND_FAILURE'
            return 'TEMPLATE_HAS_NOT_CONTENTS_VALUE OR USER_EMAIL_IS_NOT_CORRECT'
        return 'MAIL_CONFIG_DEACTIVATE'
    return obj_got
