from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.core.account.models import User
from apps.sales.task.models import OpportunityTaskSummaryDaily
from apps.shared import call_task_background
from misapi.mongo_client import mongo_log_opp_task


@shared_task
def log_task_status(
        task_id, tenant_id, company_id, employee_inherit_id,
        date_changes,
        status, status_translate,
        task_color,
):
    mongo_log_opp_task.insert_one(
        employee_inherit_id=employee_inherit_id,
        tenant_id=tenant_id,
        company_id=company_id,
        date_changes=date_changes,
        task_id=task_id,
        task_status=status,
        status_translate=status_translate,
        task_color=task_color,
    )
    return True


@shared_task
def opp_task_summary(employee_id):
    obj, _created = OpportunityTaskSummaryDaily.objects.get_or_create(employee_id=employee_id)
    obj.update_all()
    obj.save()


@shared_task
def summary_task_by_change_daily():
    date_ago = timezone.now().date() - timedelta(days=7)
    user_objs = User.objects.filter(employee_current__isnull=False, last_login__date__gte=date_ago)
    # one employee time for run is 1s
    for obj in user_objs:
        call_task_background(
            my_task=opp_task_summary,
            **{
                'employee_id': obj.employee_current_id,
            }
        )
