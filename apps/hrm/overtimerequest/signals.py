from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OvertimeRequest
from apps.shared import call_task_background
from apps.core.mailer.tasks import prepare_send_mail_new_overtime


@receiver(post_save, sender=OvertimeRequest)
def hrm_overtime_request_create(sender, instance, created, **kwargs):
    if instance.system_status == 3:
        mail_list = []
        if len(instance.empployee_list):
            mail_list = instance.empployee_list
        else:
            mail_list.append(str(instance.employee_inherit.id))
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
