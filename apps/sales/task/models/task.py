import json

from django.db import models
from django.utils import timezone

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import TASK_PRIORITY, MasterDataAbstractModel, TASK_KIND, DataAbstractModel
from .config import OpportunityTaskConfig

__all__ = ['OpportunityTask', 'OpportunityTaskStatus', 'OpportunityLogWork', 'TaskAttachmentFile']

from ..utils import TaskHandler


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
    is_finish = models.BooleanField(
        default=False,
        verbose_name='This is task finish',
    )

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
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name='Opportunity code',
        null=True,
    )
    opportunity_data = models.JSONField(
        default=dict,
        verbose_name='opportunity backup',
        null=True
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        verbose_name='Project',
        null=True,
    )
    project_data = models.JSONField(
        default=dict,
        verbose_name='project backup',
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
    percent_completed = models.SmallIntegerField(
        verbose_name='percent completed',
        default=0, null=True,
    )

    def create_code_task(self):
        # auto create code (temporary)
        if not self.code:
            code_generated = CompanyFunctionNumber.gen_code(company_obj=self.company, func=5)
            if code_generated:
                self.code = code_generated
            else:
                task = OpportunityTask.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False
                ).count()
                char = "T"
                temper = task + 1
                code = f"{char}{temper:03d}"
                self.code = code

    def update_percent(self):
        if self.task_status.is_finish:
            self.percent_completed = 100

    def before_save(self):
        self.create_code_task()
        self.update_percent()
        if self.opportunity and not self.opportunity_data:
            self.opportunity_data = {
                "id": str(self.opportunity_id),
                "title": str(self.opportunity.title),
                "code": str(self.opportunity.code),
            }
        if self.project and not self.project_data:
            self.project_data = {
                "id": str(self.project_id),
                "title": str(self.project.title),
                "code": str(self.project.code),
            }

    def save(self, *args, **kwargs):
        self.before_save()
        # opportunity log
        TaskHandler.push_opportunity_log(instance=self)
        # hit DB
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

    class Meta:
        verbose_name = 'Opportunity Attachment Task'
        verbose_name_plural = 'Opportunity Attachment Task'
        default_permissions = ()
        permissions = ()
