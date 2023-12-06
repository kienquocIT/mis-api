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
