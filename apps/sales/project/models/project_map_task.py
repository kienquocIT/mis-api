__all__ = ['ProjectMapTasks']

import json

from django.db import models

from .models import Project, ProjectWorks
from apps.shared import MasterDataAbstractModel


class ProjectMapTasks(MasterDataAbstractModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_project",
    )
    member = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_member',
        null=True
    )
    task = models.ForeignKey(
        'task.OpportunityTask',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_task',
    )
    work = models.ForeignKey(
        ProjectWorks,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_work',
        null=True,
    )
    work_before = models.JSONField(
        default=list,
        help_text=json.dumps({
            'id': "work id",
            'title': 'work title'
        }),
        verbose_name='work before',
    )

    class Meta:
        verbose_name = 'Project map task'
        verbose_name_plural = 'Project map task'
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'company', 'project')
