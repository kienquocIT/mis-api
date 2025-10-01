import json
from datetime import timedelta

from django.db import models
from django.db.models import Count
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel, update_files_is_approved
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import (
    MasterDataAbstractModel, DataAbstractModel, SimpleAbstractModel,
    TASK_PRIORITY, TASK_KIND,
)

__all__ = [
    'OpportunityTask', 'OpportunityTaskStatus', 'OpportunityLogWork', 'TaskAttachmentFile',
    'OpportunityTaskSummaryDaily', 'TaskAssigneeGroup'
]

from apps.sales.task.utils import TaskHandler


class OpportunityTaskStatus(MasterDataAbstractModel):
    title = models.CharField(verbose_name='Title Status', max_length=100)
    translate_name = models.CharField(verbose_name='Title Status translated', max_length=100)
    task_config = models.ForeignKey(
        'task.OpportunityTaskConfig',
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


class TaskAssigneeGroup(MasterDataAbstractModel):
    employee_list_access = models.JSONField(
        default=list,
        verbose_name='List of employee data backup',
        help_text=json.dumps(
            [
                {
                    'id': 'uuid4', 'full_name': 'Nguyen van A',
                    'group': {'id': 'uuid4', 'title': 'group received task group'}
                },
                {
                    'id': 'uuid4', 'full_name': 'Nguyen van B',
                    'group': {'id': 'uuid4', 'title': 'group received task group'}
                },
            ], ensure_ascii=False
        ).encode('utf8')
    )

    class Meta:
        verbose_name = 'Assignee Task group'
        verbose_name_plural = 'Assignee Task groups'
        default_permissions = ()
        permissions = ()


class OpportunityTask(DataAbstractModel):
    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return "e66cfb5a-b3ce-4694-a4da-47618f53de4c"

    task_status = models.ForeignKey(
        'task.OpportunityTaskStatus',
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
        verbose_name='attachment file of assigner',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    attach_assignee = models.JSONField(
        default=list,
        null=True,
        verbose_name='attachment file of assignee',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    percent_completed = models.SmallIntegerField(
        verbose_name='percent completed',
        default=0, null=True,
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='TaskAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='file_of_task_request',
    )
    child_task_count = models.SmallIntegerField(
        verbose_name="Number of child task",
        default=0, null=True
    )
    group_assignee = models.ForeignKey(
        TaskAssigneeGroup,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='group assignee employee',
        related_name='group_assignee_task',
    )

    def create_code_task(self):
        # auto create code (temporary)
        if not self.code:
            code_generated = CompanyFunctionNumber.auto_gen_code_based_on_config(app_code='opportunitytask')
            if code_generated:
                self.code = code_generated
            else:
                task = OpportunityTask.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False
                ).count()
                char = "TASK"
                temper = task + 1
                code = f"{char}{temper:04d}"
                self.code = code
            # include add child task count
            if self.parent_n:
                self.parent_n.child_task_count += 1
                self.parent_n.save(update_fields=['child_task_count'])

    def update_percent(self):
        if self.task_status.is_finish:
            self.percent_completed = 100

    def before_save(self):
        self.create_code_task()
        self.update_percent()
        if self.opportunity:
            self.opportunity_data = {
                "id": str(self.opportunity_id),
                "title": str(self.opportunity.title),
                "code": str(self.opportunity.code),
            }

        self.project_data = {
            "id": str(self.project_id),
            "title": str(self.project.title),
            "code": str(self.project.code),
        } if self.project else {}
        # if self.task_status.is_finish or self.percent_completed == 100:
        update_files_is_approved(
            TaskAttachmentFile.objects.filter(
                task=self, attachment__is_approved=False
            ),
            self
        )

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
        ordering = ('end_date',)
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


class TaskAttachmentFile(M2MFilesAbstractModel):
    task = models.ForeignKey(
        OpportunityTask,
        on_delete=models.CASCADE,
        verbose_name='Attachment file of task',
        related_name='task_attachment_file_task'
    )
    is_assignee_file = models.BooleanField(
        default=False,
        verbose_name='is assignee file',
        help_text='is true if this file of assignee post'
    )

    @classmethod
    def get_doc_field_name(cls):
        # field name là foreignkey của request trên bảng này
        return 'task'

    class Meta:
        verbose_name = 'Opportunity Attachment Task'
        verbose_name_plural = 'Opportunity Attachment Task'
        default_permissions = ()
        permissions = ()


class OpportunityTaskSummaryDaily(SimpleAbstractModel):  # pylint: disable=R0902
    employee = models.OneToOneField('hr.Employee', unique=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(default=timezone.now)
    state = models.PositiveSmallIntegerField(
        default=0,
        choices=(
            (0, 'wait'),
            (1, 'Ready'),
        )
    )

    actives = models.PositiveSmallIntegerField(default=0)
    overdue = models.PositiveSmallIntegerField(default=0)
    upcoming_today = models.PositiveSmallIntegerField(default=0)
    upcoming_soon = models.PositiveSmallIntegerField(default=0)
    today_created = models.PositiveSmallIntegerField(default=0)
    start_today = models.PositiveSmallIntegerField(default=0)

    by_status = models.JSONField(default=list)

    def get_detail(self):
        return {
            'actives': self.actives,
            'overdue': self.overdue,
            'upcoming_today': self.upcoming_today,
            'upcoming_soon': self.upcoming_soon,
            'today_created': self.today_created,
            'start_today': self.start_today,
            'by_status': self.by_status,
        }

    def update_all(self):
        self.update_actives(update=True, commit=False)
        self.update_overdue(update=True, commit=False)
        self.update_upcoming_today(update=True, commit=False)
        self.update_upcoming_soon(update=True, commit=False)
        self.update_today_created(update=True, commit=False)
        self.update_start_today(update=True, commit=False)
        self.update_by_status(update=True, commit=False)
        self.updated_at = timezone.now()
        self.state = 1
        return True

    def update_actives(self, update=False, commit=False):
        amount = OpportunityTask.objects.filter(employee_inherit=self.employee, percent_completed__lt=100).count()
        if update is True:
            self.actives = amount
        if commit is True:
            self.save()
        return amount

    def update_overdue(self, update=False, commit=False):
        date_now = timezone.now().date()
        amount = OpportunityTask.objects.filter(
            employee_inherit=self.employee, percent_completed__lt=100, end_date__date__lt=date_now
        ).count()
        if update is True:
            self.overdue = amount
        if commit is True:
            self.save()
        return amount

    def update_upcoming_today(self, update=False, commit=False):
        date_now = timezone.now().date()
        amount = OpportunityTask.objects.filter(
            employee_inherit=self.employee, percent_completed__lt=100, end_date__date=date_now
        ).count()
        if update is True:
            self.upcoming_today = amount
        if commit is True:
            self.save()
        return amount

    def update_upcoming_soon(self, update=False, commit=False):
        date_now = timezone.now().date() + timedelta(days=3)
        amount = OpportunityTask.objects.filter(
            employee_inherit=self.employee,
            percent_completed__lt=100,
            end_date__date__gt=date_now,
        ).count()
        if update is True:
            self.upcoming_soon = amount
        if commit is True:
            self.save()
        return amount

    def update_today_created(self, update=False, commit=False):
        date_now = timezone.now().date()
        amount = OpportunityTask.objects.filter(
            employee_inherit=self.employee, date_created__date=date_now
        ).count()
        if update is True:
            self.today_created = amount
        if commit is True:
            self.save()
        return amount

    def update_start_today(self, update=False, commit=False):
        date_now = timezone.now().date()
        amount = OpportunityTask.objects.filter(employee_inherit=self.employee, start_date__date=date_now).count()
        if update is True:
            self.start_today = amount
        if commit is True:
            self.save()
        return amount

    def update_by_status(self, update=False, commit=False):
        status_data = OpportunityTaskStatus.objects.filter(company=self.employee.company).order_by('order').values(
            'id', 'title', 'translate_name', 'task_color',
        )
        task_data = OpportunityTask.objects.filter(
            employee_inherit=self.employee, task_status_id__in=[item['id'] for item in status_data]
        ).values('task_status_id').annotate(count=Count('task_status_id'))

        data_count = {}
        for item in task_data:
            data_count[str(item['task_status_id'])] = item['count']

        data = []
        for status_detail in status_data:
            data.append({
                **status_detail,
                'id': str(status_detail['id']),
                'count': data_count.get(str(status_detail['id']), 0),
            })

        if update is True:
            self.by_status = data
        if commit is True:
            self.save()
        return data

    class Meta:
        verbose_name = 'Opportunity Task Summary Daily'
        verbose_name_plural = 'Opportunity Task Summary Daily'
        default_permissions = ()
        permissions = ()
