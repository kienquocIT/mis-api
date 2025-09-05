from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OvertimeRequest
from apps.shared import call_task_background, DisperseModel
from apps.core.mailer.mail_data import MailDataResolver
from apps.core.mailer.mail_control import SendMailController
from apps.core.mailer.tasks import get_config_template_user
from apps.core.mailer.utils import MailLogController


def send_mail_new_overtime(cls, log_cls, **kwargs):
    tenant_id = kwargs.get('tenant_id', None)
    subject = kwargs.get('subject', None)
    doc_id = kwargs.get('doc_id', None)
    doc_code = kwargs.get('doc_code', None)
    template_obj = kwargs.get('template_obj', None)
    tenant_obj = DisperseModel(app_model='tenant.Tenant').get_model().objects.filter(pk=tenant_id).first()
    email_list = kwargs.get('employee_inherit', [])
    start_date = kwargs.get('start_date', [])
    end_date = kwargs.get('end_date', [])
    start_time = kwargs.get('start_time', [])
    end_time = kwargs.get('end_time', [])
    log_cls.update(
        address_sender=cls.from_email if cls.from_email else '',
    )
    log_cls.update_employee_to(employee_to=[], address_to_init=email_list)
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
            mail_to=email_list,
            mail_cc=[],
            mail_bcc=[],
            template=template_obj.contents,
            data=MailDataResolver.new_overtime(
                tenant_obj=tenant_obj,
                doc_id=doc_id,
                app_code=doc_code,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
            ),
        )
    except Exception as err:
        state_send = False
        log_cls.update(errors_data=str(err))
    return state_send


@shared_task
def prepare_send_mail_new_overtime(data_list):
    obj_got = get_config_template_user(
        tenant_id=data_list.get('tenant_id'), company_id=data_list.get('company_id'), user_id=None, system_code=12
    )

    if not (isinstance(obj_got, list) and len(obj_got) == 3):
        return obj_got

    config_obj, template_obj, _ = obj_got

    cls = SendMailController(mail_config=config_obj, timeout=10)

    if not cls.is_active or not template_obj:
        return 'MAIL_CONFIG_DEACTIVATE'

    subject = template_obj.subject or 'New Overtime Request Received'

    log_cls = MailLogController(
        tenant_id=data_list.get('tenant_id'), company_id=data_list.get('company_id'),
        system_code=12, doc_id=data_list.get('doc_id'), subject=subject
    )

    if not log_cls.create():
        return 'SEND_FAILURE'

    state_send = send_mail_new_overtime(
        cls=cls,
        log_cls=log_cls,
        tenant_id=data_list.get('tenant_id'),
        subject=subject,
        template_obj=template_obj,
        doc_id=data_list.get('doc_id'),
        doc_code=data_list.get('doc_app'),
        employee_inherit=data_list.get('employee_inherit_email_list'),
        start_date=data_list.get('start_date'),
        end_date=data_list.get('end_date'),
        start_time=data_list.get('start_time'),
        end_time=data_list.get('end_time'),
    )

    log_cls.update(status_code=1 if state_send else 2, status_remark=state_send)
    log_cls.save()

    return 'Success' if state_send else 'SEND_FAILURE'


@receiver(post_save, sender=OvertimeRequest)
def hrm_overtime_request_create(sender, instance, created, **kwargs):
    if instance.system_status == 3:
        mail_list = []
        if len(instance.employee_list):
            lst_employee = DisperseModel(app_model='hr.employee').get_model().objects.filter(
                company_id=instance.company_id,
                id__in=instance.employee_list,
            )
            if lst_employee.count() == len(instance.employee_list):
                for emp in lst_employee:
                    if emp.email:
                        mail_list.append(emp.email)
        elif instance.employee_inherit.email:
            mail_list.append(str(instance.employee_inherit.email))
        if len(mail_list) == 0:
            print('Email not found can not send email noti overtime request')
            return True
        task_kwargs = {
            'tenant_id': str(instance.tenant_id),
            'company_id': str(instance.company_id),
            'doc_id': str(instance.id),
            'doc_app': 'overtimerequest.overtimerequest',
            'employee_inherit_email_list': mail_list,
            'start_date': instance.start_date.strftime('%Y-%m-%d'),
            'end_date': instance.end_date.strftime('%Y-%m-%d'),
            'start_time': instance.start_time.strftime('%H:%M:%S'),
            'end_time': instance.end_time.strftime('%H:%M:%S'),
        }

        if len(task_kwargs) > 0:
            call_task_background(
                my_task=prepare_send_mail_new_overtime,
                **{
                    'data_list': task_kwargs
                }
            )
        print('finish run send mail new overtime request')
