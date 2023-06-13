import datetime
from typing import Union
from uuid import UUID

from celery import shared_task

from apps.core.log.models import ActivityLog


@shared_task
def force_log_activity(
        tenant_id: Union[UUID, str, None],
        company_id: Union[UUID, str, None],
        msg: str,
        date_created: datetime.datetime,
        doc_id: Union[UUID, str, None],
        doc_app: Union[UUID, str, None],

        automated_logging: bool = False,
        request_method: Union[str, None] = None,
        user_id: Union[UUID, str, None] = None,
        employee_id: Union[UUID, str, None] = None,
        data_change: dict = None,
        change_partial: bool = False,
        task_workflow_id: Union[UUID, str, None] = None,
):
    data_change = data_change if isinstance(data_change, dict) else {}
    return ActivityLog.objects.create(
        tenant_id=tenant_id,
        company_id=company_id,
        request_method=request_method,
        date_created=date_created,
        doc_id=doc_id,
        doc_app=doc_app,
        automated_logging=automated_logging,
        user_id=user_id,
        employee_id=employee_id,
        msg=msg,
        data_change=data_change,
        change_partial=change_partial,
        task_workflow_id=task_workflow_id,
    )
