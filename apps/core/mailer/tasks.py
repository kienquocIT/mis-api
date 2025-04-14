from uuid import UUID
from celery import shared_task
from datetime import timedelta
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


def get_employee_obj(employee_id, tenant_id, company_id):
    if employee_id:
        model_emp = DisperseModel(app_model="hr.Employee").get_model()
        if model_emp and hasattr(model_emp, 'objects'):
            return model_emp.objects.filter(
                tenant_id=tenant_id, company_id=company_id, id=employee_id
            ).first()
    return None


def mail_workflow_sub(cls, log_cls, **kwargs):
    employee_obj = kwargs.get('employee_obj', None)
    subject = kwargs.get('subject', 'workflow')
    template_obj = kwargs.get('template_obj', None)
    tenant_id = kwargs.get('tenant_id', None)
    company_id = kwargs.get('company_id', None)
    runtime_id = kwargs.get('runtime_id', None)
    workflow_type = kwargs.get('workflow_type', 0)
    log_cls.update(
        address_sender=cls.from_email if cls.from_email else '',
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
            data=MailDataResolver.workflow(
                runtime_id=runtime_id, workflow_type=workflow_type,
                tenant_id=tenant_id, company_id=company_id,
            ),
        )
    except Exception as err:
        state_send = False
        log_cls.update(errors_data=str(err))
    return state_send


def mail_project_new(cls, log_cls, **kwargs):
    prj_owner_obj = kwargs.get('prj_owner_obj', None)
    prj_member_obj = kwargs.get('prj_member_obj', None)
    prj_id = kwargs.get('prj_id', None)
    subject = kwargs.get('subject', None)
    template_obj = kwargs.get('template_obj', None)
    tenant_id = kwargs.get('tenant_id', None)

    tenant_obj = DisperseModel(app_model='tenant.Tenant').get_model().objects.filter(pk=tenant_id).first()
    prj_obj = DisperseModel(app_model='project.Project').get_model().objects.filter(pk=prj_id).first()

    log_cls.update(
        address_sender=cls.from_email if cls.from_email else '',
    )
    log_cls.update_employee_to(employee_to=[], address_to_init=[prj_member_obj.email])
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
            mail_to=[prj_member_obj.email],
            template=template_obj.contents,
            data=MailDataResolver.project_new(
                tenant_obj=tenant_obj, prj_owner=prj_owner_obj, prj_member=prj_member_obj, prj_obj=prj_obj
            ),
        )
    except Exception as err:
        state_send = False
        log_cls.update(errors_data=str(err))
    return state_send


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
                            as_name=None,
                            mail_to=[user_obj.email],
                            mail_cc=[],
                            mail_bcc=[],
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
def send_email_sale_activities_email(user_id: UUID or str, email_obj):
    tenant_id = email_obj.tenant_id
    company_id = email_obj.company_id
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=user_id, system_code=0)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, _, _] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=10)
        if cls.is_active is True:
            subject = email_obj.subject

            log_cls = MailLogController(
                tenant_id=tenant_id, company_id=company_id,
                system_code=0,  # other
                doc_id=user_id, subject=subject,
            )
            log_cls.create()
            log_cls.update(
                address_sender=cls.from_email,
            )
            log_cls.update_employee_to(employee_to=[], address_to_init=email_obj.email_to_list)
            log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
            log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
            log_cls.update_log_data(host=cls.host, port=cls.port)

            try:
                state_send = cls.setup(
                    subject=subject,
                    from_email=cls.kwargs['from_email'],
                    mail_cc=email_obj.email_cc_list,
                    bcc=[],
                    header={},
                    reply_to=email_obj.employee_created.email,  # trả lời người gửi (employee created)
                ).send(
                    as_name=email_obj.employee_created.get_full_name(2),
                    mail_to=email_obj.email_to_list,
                    mail_cc=email_obj.email_cc_list,
                    mail_bcc=[],
                    template=email_obj.content,
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
def send_email_eoffice_meeting(
        user_id: UUID or str,
        meeting_obj,
        email_to_list: list,
        email_cc_list: list,
        email_bcc_list: list,
        email_subject,
        email_content,
        fpath_list: list,
):
    obj_got = get_config_template_user(
        tenant_id=meeting_obj.tenant_id,
        company_id=meeting_obj.company_id,
        user_id=user_id,
        system_code=0
    )
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, _, _] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=10)
        if cls.is_active is True:
            log_cls = MailLogController(
                tenant_id=meeting_obj.tenant_id,
                company_id=meeting_obj.company_id,
                system_code=0,  # other
                doc_id=user_id,
                subject=email_subject,
            )
            log_cls.create()
            log_cls.update(
                address_sender=cls.from_email,
            )
            log_cls.update_employee_to(employee_to=[], address_to_init=email_to_list)
            log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
            log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
            log_cls.update_log_data(host=cls.host, port=cls.port)

            try:
                state_send = cls.setup(
                    subject=email_subject,
                    from_email=cls.kwargs['from_email'],
                    mail_cc=email_cc_list,
                    bcc=email_bcc_list,
                    header={},
                    reply_to=meeting_obj.employee_created.email,  # trả lời người gửi (employee created)
                ).send(
                    as_name=meeting_obj.employee_created.get_full_name(2),
                    mail_to=email_to_list,
                    mail_cc=email_cc_list,
                    mail_bcc=email_bcc_list,
                    template=email_content,
                    data={},
                    fpath_list=fpath_list
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
def send_email_sale_activities_meeting(user_id: UUID or str, meeting_obj, is_cancel=False):
    tenant_id = meeting_obj.tenant_id
    company_id = meeting_obj.company_id
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=user_id, system_code=0)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, _, _] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=10)
        if cls.is_active is True:
            subject = meeting_obj.subject
            attended_email = [
                item.email for item in meeting_obj.employee_attended_list.all() if item.email
            ] + [
                item.email for item in meeting_obj.customer_member_list.all() if item.email
            ]

            log_cls = MailLogController(
                tenant_id=tenant_id, company_id=company_id,
                system_code=0,  # other
                doc_id=user_id, subject=subject,
            )
            log_cls.create()
            log_cls.update(
                address_sender=cls.from_email,
            )
            log_cls.update_employee_to(employee_to=[], address_to_init=attended_email)
            log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
            log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
            log_cls.update_log_data(host=cls.host, port=cls.port)

            try:
                state_send = cls.setup(
                    subject=subject,
                    from_email=cls.kwargs['from_email'],
                    mail_cc=[],
                    bcc=[],
                    header={},
                    reply_to=meeting_obj.employee_created.email,  # trả lời người gửi (employee created)
                ).send(
                    as_name=meeting_obj.employee_created.get_full_name(2),
                    mail_to=attended_email,
                    mail_cc=[],
                    mail_bcc=[],
                    template=f'<p><b>Cuộc họp mới từ {meeting_obj.employee_created.get_full_name(2)}</b></p>'
                             f'<p><b>Thời gian họp:</b> từ {meeting_obj.meeting_from_time}'
                             f' đến {meeting_obj.meeting_to_time}'
                             f' ngày {meeting_obj.meeting_date.strftime("%d/%m/%Y")}</p>'
                             f'<p><b>Địa điểm họp:</b> {meeting_obj.meeting_address}'
                             f' tại phòng {meeting_obj.room_location}</p>' if is_cancel is False else
                             f'<p><b>Thông báo huỷ cuộc họp từ {meeting_obj.employee_created.get_full_name(2)}</b></p>'
                             f'<p><b>Thời gian họp:</b> từ {meeting_obj.meeting_from_time}'
                             f' đến {meeting_obj.meeting_to_time}'
                             f' ngày {meeting_obj.meeting_date.strftime("%d/%m/%Y")}</p>'
                             f'<p><b>Địa điểm họp:</b> {meeting_obj.meeting_address}'
                             f' tại phòng {meeting_obj.room_location}</p>',
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
                                as_name=None,
                                mail_to=[user_obj.email],
                                mail_cc=[],
                                mail_bcc=[],
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
                    as_name=None,
                    mail_to=to_main,
                    mail_cc=[],
                    mail_bcc=[],
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
                as_name=None,
                mail_to=to_mail,
                mail_cc=[],
                mail_bcc=[],
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
        employee_id,
        runtime_id,
        workflow_type,
):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=user_id, system_code=6)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, template_obj, user_obj] = obj_got
        cls = SendMailController(mail_config=config_obj, timeout=3)
        employee_obj = get_employee_obj(employee_id=employee_id, tenant_id=tenant_id, company_id=company_id)
        if cls.is_active is True and template_obj and user_obj and employee_obj:
            if template_obj.contents and user_obj.email and employee_obj.email:
                subject = template_obj.subject if template_obj.subject else 'Workflow'
                log_cls = MailLogController(
                    tenant_id=tenant_id, company_id=company_id,
                    system_code=6,  # WORKFLOW
                    doc_id=user_id, subject=subject,
                )
                if log_cls.create():
                    state_send = mail_workflow_sub(
                        cls=cls, log_cls=log_cls,
                        **{
                            'employee_obj': employee_obj,
                            'subject': subject,
                            'template_obj': template_obj,
                            'tenant_id': tenant_id,
                            'company_id': company_id,
                            'runtime_id': runtime_id,
                            'workflow_type': workflow_type,
                        }
                    )
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


@shared_task
def send_mail_new_project_member(tenant_id, company_id, prj_owner, prj_member, prj_id):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=None, system_code=7)
    if isinstance(obj_got, list) and len(obj_got) == 3:
        [config_obj, template_obj, user_obj] = obj_got
        print('user_obj', user_obj)
        cls = SendMailController(mail_config=config_obj, timeout=3)
        prj_owner_obj = get_employee_obj(employee_id=prj_owner, tenant_id=tenant_id, company_id=company_id)
        prj_member_obj = get_employee_obj(employee_id=prj_member, tenant_id=tenant_id, company_id=company_id)

        if cls.is_active is True and template_obj and prj_owner_obj and prj_member_obj:
            if template_obj.contents and prj_member_obj.email and prj_owner_obj.email:
                subject = template_obj.subject if template_obj.subject else 'New Project Create'
                log_cls = MailLogController(
                    tenant_id=tenant_id, company_id=company_id,
                    system_code=7,  # PROJECT
                    doc_id=prj_id, subject=subject,
                )
                if log_cls.create():
                    state_send = mail_project_new(
                        cls=cls, log_cls=log_cls,
                        **{
                            'prj_owner_obj': prj_owner_obj,
                            'prj_member_obj': prj_member_obj,
                            'prj_id': prj_id,
                            'subject': subject,
                            'template_obj': template_obj,
                            'tenant_id': tenant_id
                        }
                    )
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


@shared_task
def send_mail_new_contract_submit(
        tenant_id, company_id, assignee_id, employee_created_id, contract_id, signature_runtime_id
):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=None, system_code=8)

    if not (isinstance(obj_got, list) and len(obj_got) == 3):
        return obj_got

    config_obj, template_obj, _ = obj_got

    cls = SendMailController(mail_config=config_obj, timeout=3)

    if not cls.is_active or not template_obj:
        return 'MAIL_CONFIG_DEACTIVATE'

    assignee = get_employee_obj(employee_id=assignee_id, tenant_id=tenant_id, company_id=company_id)
    employee_created = get_employee_obj(employee_id=employee_created_id, tenant_id=tenant_id, company_id=company_id)

    if not (assignee and assignee.email and employee_created and employee_created.email and template_obj.contents):
        return 'TEMPLATE_HAS_NOT_CONTENTS_VALUE OR USER_EMAIL_IS_NOT_CORRECT'

    subject = template_obj.subject or 'New request signing to contract'

    log_cls = MailLogController(
        tenant_id=tenant_id, company_id=company_id,
        system_code=8, doc_id=contract_id, subject=subject
    )

    if not log_cls.create():
        return 'SEND_FAILURE'

    state_send = mail_request_signing(
        cls=cls, log_cls=log_cls,
        tenant_id=tenant_id, subject=subject,
        assignee=assignee, employee_created=employee_created,
        contract_id=contract_id, template_obj=template_obj,
        signature_runtime_id=signature_runtime_id
    )

    log_cls.update(status_code=1 if state_send else 2, status_remark=state_send)
    log_cls.save()

    return 'Success' if state_send else 'SEND_FAILURE'


def mail_request_signing(cls, log_cls, **kwargs):
    tenant_id = kwargs.get('tenant_id', None)
    subject = kwargs.get('subject', None)
    assignee = kwargs.get('assignee', None)
    employee_created = kwargs.get('employee_created', None)
    contract = kwargs.get('contract_id', None)
    template_obj = kwargs.get('template_obj', None)
    signature_runtime_id = kwargs.get('signature_runtime_id', None)

    tenant_obj = DisperseModel(app_model='tenant.Tenant').get_model().objects.filter(pk=tenant_id).first()
    contract_obj = DisperseModel(app_model='employeeinfo.EmployeeContract').get_model().objects.filter(
        pk=contract
    ).first()
    log_cls.update(
        address_sender=cls.from_email if cls.from_email else '',
    )
    log_cls.update_employee_to(employee_to=[], address_to_init=[assignee.email])
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
            as_name='No Reply',
            mail_to=[assignee.email],
            mail_cc=[],
            mail_bcc=[],
            template=template_obj.contents,
            data=MailDataResolver.new_contract(
                tenant_obj=tenant_obj, assignee=assignee, employee_created=employee_created, contract=contract_obj,
                signature_runtime=signature_runtime_id
            ),
        )
    except Exception as err:
        state_send = False
        log_cls.update(errors_data=str(err))
    return state_send


@shared_task
def send_mail_annual_leave(leave_id, tenant_id, company_id, employee_id, email_lst):
    obj_got = get_config_template_user(tenant_id=tenant_id, company_id=company_id, user_id=None, system_code=9)

    if not (isinstance(obj_got, list) and len(obj_got) == 3):
        return obj_got

    config_obj, template_obj, _ = obj_got

    cls = SendMailController(mail_config=config_obj, timeout=3)

    if not cls.is_active or not template_obj:
        return 'MAIL_CONFIG_DEACTIVATE'

    employee_off = get_employee_obj(employee_id=employee_id, tenant_id=tenant_id, company_id=company_id)
    employee_lead = employee_off.group.first_manager
    if not employee_lead:
        employee_lead = employee_off.group.second_manager
    employee_info = {
        'full_name': employee_lead.get_full_name() if employee_lead else _("Missing info"),
        'email': employee_lead.email if employee_lead else _("Missing info")
    }

    if not (employee_off and employee_off.email and template_obj.contents):
        return 'TEMPLATE_HAS_NOT_CONTENTS_VALUE OR USER_EMAIL_IS_NOT_CORRECT'

    subject = template_obj.subject or 'New leave approved'

    log_cls = MailLogController(
        tenant_id=tenant_id, company_id=company_id,
        system_code=9, doc_id=leave_id, subject=subject
    )

    if not log_cls.create():
        return 'SEND_FAILURE'
    log_cls.update(
        address_sender=cls.from_email if cls.from_email else '',
    )
    log_cls.update_employee_to(employee_to=[], address_to_init=[employee_off.email])
    log_cls.update_employee_cc(employee_cc=[], address_cc_init=cls.kwargs['cc_email'])
    log_cls.update_employee_bcc(employee_bcc=[], address_bcc_init=cls.kwargs['bcc_email'])
    log_cls.update_log_data(host=cls.host, port=cls.port)

    tenant_obj = DisperseModel(app_model='core.Tenant').get_model()
    tenant_obj = tenant_obj.objects.get(id=tenant_id)
    leave_obj = DisperseModel(app_model='eoffice.LeaveRequest').get_model()
    leave_obj = leave_obj.objects.get(id=leave_id)
    date_back = (leave_obj.start_day + timedelta(leave_obj.total)).strftime("%d/%m/%Y")
    try:
        state_send = cls.setup(
            subject=subject,
            from_email=cls.kwargs['from_email'],
            mail_cc=cls.kwargs['cc_email'],
            bcc=cls.kwargs['bcc_email'],
            header={},
            reply_to=cls.kwargs['reply_email'],
        ).send(
            as_name=employee_off.email,
            # mail_to=[employee_off.email, *email_lst],
            mail_to=["mailcviec01@gmail.com", 'mailcviec03@gmail.com'],
            mail_cc=[],
            mail_bcc=[],
            template=template_obj.contents,
            data=MailDataResolver.new_leave_approved(
                tenant_obj=tenant_obj, employee=employee_off, day_off=leave_obj.total, date_back=date_back,
                link_id=leave_id, employee_lead=employee_info
            ),
        )
        print('email lst: ', [employee_off.email, *email_lst])
    except Exception as err:
        state_send = False
        log_cls.update(errors_data=str(err))

    log_cls.update(status_code=1 if state_send else 2, status_remark=state_send)
    log_cls.save()

    return 'Success' if state_send else 'SEND_FAILURE'
