import datetime
from typing import Union
from uuid import UUID

from celery import shared_task
from django.utils import timezone

from apps.core.log.models import (
    ActivityLog,
    Notifications,
)

__all__ = [
    'force_log_activity',
    'force_new_notify',
    'force_new_notify_many',
]


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
    obj = ActivityLog.objects.create(
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
    return str(obj)


@shared_task
def force_new_notify(
        tenant_id: Union[UUID, str, None],
        company_id: Union[UUID, str, None],
        title: str,
        msg: str,
        date_created: datetime.datetime,
        doc_id: Union[UUID, str, None],
        doc_app: Union[UUID, str, None],
        user_id: Union[UUID, str, None] = None,
        employee_id: Union[UUID, str, None] = None,
        employee_sender_id: Union[UUID, str, None] = None,

        is_submit: bool = True,
):
    obj = Notifications(
        tenant_id=tenant_id,
        company_id=company_id,
        title=title if len(title) <= 100 else f'{title[:97]}...',
        msg=msg,
        date_created=date_created if date_created else timezone.now(),
        doc_id=doc_id,
        doc_app=doc_app,
        user_id=user_id,
        employee_id=employee_id,
        employee_sender_id=employee_sender_id,
        is_done=False,
    )
    obj.before_save(force_insert=True)
    if is_submit:
        return obj.save()
    return str(obj)


@shared_task
def force_new_notify_many(data_list: list[dict[str, any]]):
    # data_list[index] is ARGS of "force_new_notify" exclude args name "is_submit"
    arr_objs = []
    for item in data_list:
        arr_objs.append(
            force_new_notify(
                **item, is_submit=False
            )
        )
    objs = Notifications.objects.bulk_create(arr_objs)
    return str(objs)
