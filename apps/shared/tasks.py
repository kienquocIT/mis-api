import time

import celery
import json
from typing import Union
from uuid import uuid4

from celery import shared_task
from misapi import celery_app
from celery.utils.log import get_task_logger
from django.conf import settings
from django_celery_results.models import TaskResult

logger = get_task_logger(__name__)

__all__ = ['call_task_background']


def call_task_background(my_task: callable, *args, **kwargs) -> Union[Exception, bool]:
    """
    Function support call task with async. Then update args and kwargs of log records by Task ID.
    """
    countdown = kwargs.pop('countdown', 0)

    if isinstance(my_task, celery.Task):
        if settings.CELERY_TASK_ALWAYS_EAGER is True:
            return my_task(*args, **kwargs)
        _id = str(uuid4())
        my_task.apply_async(
            args=args, kwargs=kwargs,
            task_id=_id,
            link=my_task_result.s(
                _id, task_path=str(f'{my_task.__module__}.{my_task.__name__}'), task_args=args, task_kwargs=kwargs
            ),
            countdown=countdown,
        )
        return True
    raise AttributeError('my_task must be celery task function that have decorator is shared_task')


@shared_task(ignore_result=True, default_retry_delay=10, max_retries=3)  # default_retry_delay: seconds
def my_task_result(sender, task_id, task_path, task_args, task_kwargs):
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
        task_result.task_name = task_path
        task_result.task_args = json.dumps(task_args)
        task_result.task_kwargs = json.dumps(task_kwargs)
        task_result.save()
        return True
    except Exception as err:
        raise my_task_result.retry(exc=err)
