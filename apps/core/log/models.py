from uuid import uuid4

from django.db import models
from django.db.models import Manager
from django.utils import timezone

__all__ = [
    'ActivityLog',
]


class ActivityLog(models.Model):
    # base field
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )

    # feature field
    request_method = models.CharField(
        max_length=10,
        null=True,
        verbose_name='HTTP method of Log',
        help_text='choices in: GET, POST, PUT, DELETE, ...'
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    doc_id = models.UUIDField(
        null=True,
        verbose_name='ID of Object',
        help_text="Null if it is log's general; otherwise, The value of ID field is required."
    )
    doc_app = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='App Code of Object',
        help_text='Format: {app_label}.{model_name}; '
                  'It is empty when doc_id is null, otherwise the value is required to match the format.',
    )
    automated_logging = models.BooleanField(
        verbose_name='Is automated logging',
        help_text='Correct if it is an automated system log; '
                  'otherwise, the values of the user and employee fields must have a value.'
    )
    user = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='This user is performer'
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='This employee is performer'
    )
    msg = models.TextField(
        blank=True,
        verbose_name='Message was logged',
        help_text='Messages was translated before save'
    )
    data_change = models.JSONField(
        default=dict,
        verbose_name='Request Body',
        help_text='JSON send from client for POST,PUT'
    )
    change_partial = models.BooleanField(
        default=False,
        verbose_name='Flag partial of Mixins',
    )
    task_workflow = models.ForeignKey(
        'workflow.RuntimeAssignee',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Task Workflow ID',
        help_text='It is None when update in doc; Otherwise, Update have exist Zone WF'
    )

    # backup data
    user_data = models.JSONField(
        default=dict,
        verbose_name='User backup data',
    )
    employee_data = models.JSONField(
        default=dict,
        verbose_name='Employee backup data',
    )

    objects = Manager()

    def __str__(self):
        return f'Doc -> {self.doc_id} - {self.doc_app} : ' \
               f'Actor -> {self.user_id} - {self.employee_id} : ' \
               f'Logged -> {self.automated_logging} - {self.msg}'

    def before_save(self, force_insert):
        if force_insert is True:
            if self.user:
                self.user_data = {
                    'id': str(self.user_id),
                    'first_name': str(self.user.first_name),
                    'last_name': str(self.user.last_name),
                    'full_name': str(self.user.get_full_name()),
                    'email': str(self.user.email),
                    'phone': str(self.user.phone),
                    'last_login': str(self.user.last_login),
                }
            if self.employee:
                self.employee_data = {
                    'id': str(self.employee_id),
                    'first_name': str(self.employee.first_name),
                    'last_name': str(self.employee.last_name),
                    'full_name': str(self.employee.get_full_name()),
                    'email': str(self.employee.email),
                    'phone': str(self.employee.phone),
                    'avatar': str(self.employee.avatar),
                }
            if self.request_method:
                self.request_method = self.request_method.upper()
        return True

    def save(self, *args, **kwargs):
        self.before_save(force_insert=kwargs.get('force_insert', False))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Log Activity'
        verbose_name_plural = 'Log Activity'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
        indexes = [
            models.Index(fields=['doc_id']),
            models.Index(fields=['doc_app']),
            models.Index(fields=['doc_id', 'doc_app']),
        ]
