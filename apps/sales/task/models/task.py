import json
import uuid

from django.db import models
from django.utils import timezone

from apps.shared import TASK_PRIORITY, MasterDataAbstractModel, TASK_KIND, DataAbstractModel
from apps.sales.opportunity.models import Opportunity
from .config import OpportunityTaskConfig

__all__ = ['OpportunityTask', 'OpportunityTaskStatus', 'OpportunityLogWork', 'TaskAttachmentFile']


class OpportunityTaskStatus(MasterDataAbstractModel):
    title = models.CharField(verbose_name='Title Status', max_length=100)
    translate_name = models.CharField(verbose_name='Title Status translated', max_length=100)
    task_config = models.ForeignKey(
        OpportunityTaskConfig,
        on_delete=models.CASCADE,
        verbose_name='Task Config',
    )
    order = models.SmallIntegerField(
        default=1
    )
    is_edit = models.BooleanField(
        default=True,
        verbose_name='User can edit or not',
    )
    task_kind = models.SmallIntegerField(
        choices=TASK_KIND,
        default=0,
    )
    task_color = models.CharField(verbose_name='Status color', max_length=100, default=None, null=True)

    class Meta:
        verbose_name = 'Task Status'
        verbose_name_plural = 'Task Status'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class OpportunityTask(DataAbstractModel):
    task_status = models.ForeignKey(
        OpportunityTaskStatus,
        on_delete=models.CASCADE,
        verbose_name='Task status',
    )
    start_date = models.DateTimeField(
        verbose_name='Start Date', null=True
    )
    end_date = models.DateTimeField(
        verbose_name='End Date', null=True
    )
    estimate = models.CharField(
        max_length=10,
        verbose_name='Estimate Time', null=True
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        verbose_name='Opportunity code',
        null=True,
    )
    opportunity_data = models.JSONField(
        default=dict,
        verbose_name='opportunity backup',
        null=True
    )
    priority = models.SmallIntegerField(
        choices=TASK_PRIORITY,
        default=0,
    )
    label = models.JSONField(
        default=list,
        verbose_name='Tag label',
        null=True
    )
    assign_to = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
        related_name='opportunity_task_assign_to',
    )
    remark = models.TextField(blank=True)

    checklist = models.JSONField(
        default=list,
        verbose_name='Checklist',
        null=True,
        help_text=json.dumps(
            [
                {"name": "read document", "done": False}
            ]
        )
    )
    parent_n = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Sub-task of parent task'
    )
    log_time = models.JSONField(
        default=list,
        verbose_name='self employee log time after create task',
        null=True,
        help_text=json.dumps(
            {
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "time_spent": 'eg. 3w 4d 12h'
            }
        )
    )
    attach = models.JSONField(
        default=list,
        null=True,
        verbose_name='attachment file',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )

    def create_code_task(self):
        # auto create code (temporary)
        task = OpportunityTask.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        if not self.code:
            char = "T"
            temper = task + 1
            code = f"{char}{temper:03d}"
            self.code = code

    def before_save(self):
        self.create_code_task()
        if self.opportunity and not self.opportunity_data:
            self.opportunity_data = {
                "id": str(self.opportunity_id),
                "title": str(self.opportunity.title),
                "code": str(self.opportunity.code),
            }
        if self.assign_to and not self.employee_inherit:
            self.employee_inherit = self.assign_to

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Opportunity Task Log Work'
        verbose_name_plural = 'Opportunity Task Log Work'
        default_permissions = ()
        ordering = ('date_created',)
        permissions = ()


class OpportunityLogWork(MasterDataAbstractModel):
    start_date = models.DateTimeField(
        verbose_name='Start Date'
    )
    end_date = models.DateTimeField(
        verbose_name='End Date'
    )
    time_spent = models.CharField(
        max_length=10,
        verbose_name='Time spent'
    )
    task = models.ForeignKey(
        OpportunityTask,
        on_delete=models.CASCADE,
        verbose_name='Opportunity Task',
    )
    employee_created = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.CASCADE,
        help_text='Employee log work',
        related_name='opportunity_log_work_employee_created',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'Opportunity Task Log Work'
        verbose_name_plural = 'Opportunity Task Log Work'
        default_permissions = ()
        permissions = ()


class TaskAttachmentFile(MasterDataAbstractModel):
    attachment = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Task attachment files',
        help_text='Task had one/many attachment file',
        related_name='task_attachment_file',
    )
    task = models.ForeignKey(
        OpportunityTask,
        on_delete=models.CASCADE,
        verbose_name='Attachment file of task'
    )
    order = models.SmallIntegerField(
        default=1
    )
    media_file = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        verbose_name = 'Opportunity Attachment Task'
        verbose_name_plural = 'Opportunity Attachment Task'
        default_permissions = ()
        permissions = ()
