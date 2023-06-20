from django.db import models

from .config import TaskConfig
from apps.shared import DataAbstractModel, SimpleAbstractModel


class TaskStatus(SimpleAbstractModel):
    title = models.CharField(verbose_name='Title Status', max_length=100)
    translate_name = models.CharField(verbose_name='Title Status translated', max_length=100)
    task_config = models.ForeignKey(
        TaskConfig,
        on_delete=models.CASCADE,
        verbose_name='Task Config',
    )

    class Meta:
        verbose_name = 'Task Status'
        verbose_name_plural = 'Task Status'
        default_permissions = ()
        permissions = ()


class OrderDeliverySub(DataAbstractModel):
    task_code = models.CharField(
        max_length=100,
        verbose_name='User input code'
    )
