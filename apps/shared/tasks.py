import json
from typing import Union

import celery

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django_celery_results.models import TaskResult

logger = get_task_logger(__name__)

__all__ = ['call_task_background']


def call_task_background(my_task: callable, *args, **kwargs) -> Union[Exception, bool]:
    """
    Function support call task with async. Then update args and kwargs of log records by Task ID.
    """
    if isinstance(my_task, celery.Task):
        if settings.CELERY_TASK_ALWAYS_EAGER is True:
            return my_task(*args, **kwargs)
        result = my_task.apply_async(args=args, kwargs=kwargs)
        my_task_result.delay(result.id, args, kwargs)
        return True
    raise AttributeError('my_task must be celery task function that have decorator is shared_task')


@shared_task(ignore_result=True)
def my_task_result(task_id, task_args: list, task_kwargs: dict):
    """
    Function task support update arguments and keyword arguments to record TASK ID
    (fix middle django-celery-results not workings)

    Returns:
        True: Update successful.
        False: Update failure.

    Notes:
        This task don't add new record to TaskResult table. (ignore_result=True)
    """
    try:
        task_result = TaskResult.objects.get(task_id=task_id)

        task_result.task_args = json.dumps(task_args)
        task_result.task_kwargs = json.dumps(task_kwargs)
        task_result.save()
        return True
    except TaskResult.DoesNotExist:
        log_msg = '[ID={task_id}] Update arguments and keyword arguments failed. '
        log_msg += 'Content: args={task_args} | kwargs={task_kwargs}'
        logger.error(log_msg)
    return False
