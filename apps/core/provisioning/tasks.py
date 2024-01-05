import time

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def testing_task(msg, abc, *args, **kwargs):
    msg_log = 'CELERY LOG: ' + msg + ' ' + abc
    print(msg_log)
    logger.info(msg_log)
    time.sleep(10)
    return {'returned': True}
