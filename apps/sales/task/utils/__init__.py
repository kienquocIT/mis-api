import sys
import traceback
from celery import shared_task
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.sales.opportunity.models import OpportunityActivityLogTask, OpportunityActivityLogs


@shared_task
def task_create_opportunity_activity_log(subject, opps, task):
    try:
        activity = OpportunityActivityLogTask.objects.create(
            subject=subject,
            opportunity_id=opps,
            task_id=task,
            activity_name=_('Task'),
            activity_type='task'
        )
        if activity:
            log = OpportunityActivityLogs.objects.create(
                call=None,
                email=None,
                meeting=None,
                task=activity,
                opportunity=activity.opportunity,
                log_type=1,
            )
            if log:
                return True, ''
        return False, 'Task object not found'
    except Exception as err:
        if settings.DEBUG is True:
            traceback.print_exc()
            print(f'Error on line {sys.exc_info()[-1].tb_lineno} with {str(err)}')
        return False, 'Task object not found'


class TaskHandler:

    # OPPORTUNITY LOG
    @classmethod
    def push_opportunity_log(cls, instance):
        if instance.opportunity:
            OpportunityActivityLogs.push_opportunity_log(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                opportunity_id=instance.opportunity_id,
                employee_created_id=instance.employee_created_id,
                app_code=str(instance.__class__.get_model_code()),
                doc_id=instance.id,
                log_type=1,
                doc_data={
                    'id': str(instance.id),
                    'title': instance.title,
                    'code': instance.code,
                    'task_status': instance.task_status.title if instance.task_status else 'To do',
                    'date_created': str(instance.date_created),
                }
            )
        return True
