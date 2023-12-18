from typing import Union
from uuid import uuid4

from celery import Task
from celery.utils.log import get_task_logger

from django.conf import settings

from misapi import celery_app

logger = get_task_logger(__name__)

__all__ = ['call_task_background', 'check_active_celery_worker']


def call_task_background(my_task: callable, *args, **kwargs) -> Union[Exception, bool]:
    """
    Function support call task with async. Then update args and kwargs of log records by Task ID.
    countdown: seconds
    """

    if settings.DEBUG_BG_TASK:
        print('[T] call_task_background   : ', getattr(my_task, 'name', '**TASK_NAME_FAIL**'), args, kwargs)

    countdown = kwargs.pop('countdown', 0)
    _id = kwargs.pop('task_id', str(uuid4()))
    if isinstance(my_task, Task):
        if settings.CELERY_TASK_ALWAYS_EAGER is True:
            return my_task(*args, **kwargs)
        my_task.apply_async(
            args=args, kwargs=kwargs,
            task_id=_id,
            # link=my_task_result.s(
            #     _id,
            #     task_path=str(f'{my_task.__module__}.{my_task.__name__}'),
            #     task_args=json.dumps(args, cls=CustomizeEncoder),
            #     task_kwargs=json.dumps(kwargs, cls=CustomizeEncoder),
            # ),
            countdown=countdown,
        )
        return _id
    raise AttributeError('my_task must be celery task function that have decorator is shared_task')


# @shared_task(ignore_result=True, default_retry_delay=10, max_retries=3)  # default_retry_delay: seconds
# def my_task_result(sender, task_id, task_path, task_args, task_kwargs):  # pylint: disable=W0613
#     """
#     Function task support update arguments and keyword arguments to record TASK ID
#     (fix middle django-celery-results not workings)
#
#     Returns:
#         True: Update successful.
#         False: Update failure.
#
#     Notes:
#         This task don't add new record to TaskResult table. (ignore_result=True)
#     """
#     try:
#         task_result = TaskResult.objects.get(task_id=task_id)
#         task_result.task_name = str(task_path)
#         task_result.task_args = str(task_args)
#         task_result.task_kwargs = str(task_kwargs)
#         task_result.save()
#         return True
#     except Exception as err:
#         raise my_task_result.retry(exc=err)


def check_active_celery_worker():
    try:
        state = celery_app.control.inspect().active()
        if state:
            return True
    except Exception as err:
        print(err)
    return False
