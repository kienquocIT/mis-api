__all__ = ['ProjectMapTasks']

import json

from django.db import models

from apps.shared import MasterDataAbstractModel
from .models import Project, ProjectWorks


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
        default=dict,
        help_text=json.dumps({
            'id': "work id",
            'title': 'work title'
        }),
        verbose_name='work before',
    )

    def before_save(self):
        if self.work and not self.work_before:
            self.work_before = {
                "id": str(self.work_id),
                "title": self.work.title
            }
        return True

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project map task'
        verbose_name_plural = 'Project map task'
        default_permissions = ()
        permissions = ()
        ordering = ('-date_created',)
        unique_together = ('project', 'task')
