from typing import Union
from uuid import UUID

from celery import shared_task
from django.apps import apps

__all__ = [
    'call_log_update_at_zone',
]


@shared_task
def call_log_update_at_zone(task_id: Union[UUID, str], employee_id: Union[UUID, str], is_system: bool = False):
    rt_assignee = apps.get_model(
        app_label='workflow', model_name='runtimeassignee'
    ).objects.get(pk=task_id)
    apps.get_model(
        app_label='workflow', model_name='runtimelog'
    ).objects.create(
        actor_id=employee_id,
        runtime=rt_assignee.stage.runtime,
        stage=rt_assignee.stage,
        kind=1,  # in doc
        action=0,
        msg='Update data at zone',
        is_system=is_system,
    )
    rt_assignee.action_perform.append('update')
    rt_assignee.action_perform = list(set(rt_assignee.action_perform))
    rt_assignee.save(update_fields=['action_perform'])
    return rt_assignee
