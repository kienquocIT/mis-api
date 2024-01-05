import logging

from typing import Union
from uuid import UUID

from celery import shared_task
from django.db import models

from apps.core.workflow.models import (
    Runtime, RuntimeStage, RuntimeAssignee,
)
from apps.core.workflow.utils.runtime import (
    RuntimeStageHandler, RuntimeHandler,
)
from apps.shared import DisperseModel, DataAbstractModel, call_task_background

logger = logging.getLogger(__name__)

__all__ = [
    'call_new_runtime',
    'call_next_stage',
    'call_approval_task',
    'decorator_run_workflow',
]


def decorator_run_workflow(func):
    def wrapper(*args, **kwargs):
        instance = func(*args, **kwargs)
        if isinstance(instance, DataAbstractModel):
            try:
                if instance.system_status == 1:
                    if not instance.workflow_runtime_id:
                        if not Runtime.objects.filter(
                                tenant_id=instance.tenant_id, company_id=instance.company_id,
                                doc_id=instance.id, app_code=str(instance.__class__.get_model_code())
                        ).exists():
                            runtime_obj = RuntimeHandler.create_runtime_obj(
                                tenant_id=str(instance.tenant_id), company_id=str(instance.company_id),
                                doc_id=str(instance.id), app_code=str(instance.__class__.get_model_code()),
                                employee_created=instance.employee_created,
                                employee_inherit=instance.employee_inherit,
                            )
                            call_task_background(
                                call_new_runtime,
                                *[str(runtime_obj.id)],
                                **{'countdown': 2}
                            )
            except Exception as err:
                msg = f'[decorator_run_workflow] Errors: {str(err)}, instance: {str(instance)}'
                print(msg)
                logger.error(msg)
        return instance

    return wrapper


@shared_task
def call_new_runtime(runtime_id: str):
    runtime_obj = Runtime.objects.get(pk=runtime_id)
    if runtime_obj:
        return RuntimeStageHandler(runtime_obj=runtime_obj).apply(app_obj=runtime_obj.app)
    return logger.error('Runtime Obj does not exist. runtime_id: %s', str(str(runtime_id)))


@shared_task
def call_next_stage(runtime_id: Union[UUID, str], stage_currently_id: Union[UUID, str]):
    # get objects from arguments
    runtime_obj = Runtime.objects.get(pk=runtime_id)
    stage_currently_obj = RuntimeStage.objects.get(pk=stage_currently_id)

    # new cls call run_next
    cls_handle = RuntimeStageHandler(
        runtime_obj=runtime_obj,
    )
    return cls_handle.run_next(
        workflow=runtime_obj.flow, stage_obj_currently=stage_currently_obj
    )


@shared_task
def call_approval_task(
        runtime_assignee_id: RuntimeAssignee, employee_id: models.Model, action_code: int,
        remark: str, next_node_collab_id: Union[UUID, str],
):
    runtime_assignee_obj = RuntimeAssignee.objects.get(pk=runtime_assignee_id)
    employee_obj = DisperseModel(app_model='hr.employee').get_model().objects.get(pk=employee_id)
    return RuntimeHandler().action_perform(
        rt_assignee=runtime_assignee_obj,
        employee_assignee_obj=employee_obj,
        action_code=action_code,
        remark=remark,  # use for action return
        next_node_collab_id=next_node_collab_id,  # use for action approve if next node is OUT FORM node
    )
