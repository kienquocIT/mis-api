import json
from uuid import uuid4

from django.db import models
from django.db.models import Manager
from django.utils import timezone

__all__ = [
    'ActivityLog',
    'Notifications',
    'BookMark',
    'DocPined',
    'MailLog',
]

BOOKMARKS_KIND = (
    (0, 'View Name'),
    (1, 'Custom URL')
)


def parse_backup_user(user_obj) -> dict:
    if user_obj:
        return {
            'id': str(user_obj.id),
            'first_name': str(user_obj.first_name),
            'last_name': str(user_obj.last_name),
            'full_name': str(user_obj.get_full_name()),
            'email': str(user_obj.email),
            'phone': str(user_obj.phone),
            'last_login': str(user_obj.last_login),
        }
    return {}


def parse_backup_employee(employee_obj) -> dict:
    if employee_obj:
        return {
            'id': str(employee_obj.id),
            'first_name': str(employee_obj.first_name),
            'last_name': str(employee_obj.last_name),
            'full_name': str(employee_obj.get_full_name()),
            'email': str(employee_obj.email),
            'phone': str(employee_obj.phone),
            'avatar_img': str(employee_obj.avatar_img),
        }
    return {}


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
                self.user_data = parse_backup_user(self.user)
            if self.employee:
                self.employee_data = parse_backup_employee(self.employee)
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


class Notifications(models.Model):
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
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    user = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='This user is performer',
        related_name='notifies_of_user',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='This employee is performer',
        related_name='notifies_of_employee',
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Title of Doc',
    )
    msg = models.TextField(
        blank=True,
        verbose_name='Message of notify',
    )

    # Object related
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

    # Flag
    automated_sending = models.BooleanField(
        default=True,
        verbose_name='Is automated sending',
        help_text='Correct if it is an automated system log; '
                  'otherwise, the values of the user and employee fields must have a value.'
    )
    employee_sender = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Sender',
        help_text='This employee sent notify',
        related_name='notifies_send_by_employee',
    )
    is_done = models.BooleanField(
        default=False,
        verbose_name='Is Read notify',
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
    employee_sender_data = models.JSONField(
        default=dict,
        verbose_name='Employee sender backup data',
    )

    @staticmethod
    def cache_base_key(user_obj=None, my_obj=None):
        if user_obj:
            return f'{user_obj.tenant_current_id}_{user_obj.company_current_id}_{user_obj.employee_current_id}_True'
        if my_obj:
            return f'{my_obj.tenant_id}_{my_obj.company_id}_{my_obj.employee_id}_True'
        raise ValueError('Need user_obj or my_obj has value.')

    @classmethod
    def call_seen_all(cls, tenant_id, company_id, employee_id):
        cls.objects.filter(tenant_id=tenant_id, company_id=company_id, employee_id=employee_id, is_done=False).update(
            is_done=True
        )
        return True

    @classmethod
    def call_clean_all_seen(cls, tenant_id, company_id, employee_id):
        cls.objects.filter(tenant_id=tenant_id, company_id=company_id, employee_id=employee_id, is_done=True).delete()
        return True

    def __str__(self):
        return f'Doc -> {self.doc_id} - {self.doc_app} : Actor -> {self.user_id} - {self.employee_id}'

    def before_save(self, force_insert):
        if force_insert is True:
            if self.user:
                self.user_data = parse_backup_user(self.user)
            if self.employee:
                self.employee_data = parse_backup_employee(self.employee)
            if self.employee_sender:
                self.employee_sender_data = parse_backup_employee(self.employee_sender)
        return True

    def save(self, *args, **kwargs):
        self.before_save(force_insert=kwargs.get('force_insert', False))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Notifications'
        verbose_name_plural = 'Notifications'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
        indexes = [
            models.Index(fields=['tenant_id', 'company_id', 'employee_id']),
            models.Index(fields=['tenant_id', 'company_id', 'employee_id', 'is_done']),
        ]


class BookMark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='This employee is performer',
        related_name='bookmarks_of_employee',
    )
    title = models.CharField(
        max_length=20,
        verbose_name='Title of BookMark'
    )
    kind = models.PositiveSmallIntegerField(
        choices=BOOKMARKS_KIND,
        verbose_name='Type of Bookmarks',
        help_text=json.dumps(BOOKMARKS_KIND),
    )
    view_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='View Name UI'
    )
    customize_url = models.TextField(
        null=True,
        blank=True,
        verbose_name='User URL Custom'
    )
    box_style = models.JSONField(
        default=dict,
        verbose_name='Style of Box display',
        help_text=json.dumps(
            {
                'icon_cls': '',
                'bg_cls': '',
                'text_cls': '',
            }
        )
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Order of BookMark Display',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'BookMark'
        verbose_name_plural = 'BookMark'
        ordering = ('order', '-date_created')
        default_permissions = ()
        permissions = ()


class DocPined(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.CASCADE,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.CASCADE,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    # real field
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='This employee is performer',
        related_name='pined_of_employee',
    )
    title = models.TextField(
        blank=True,
        verbose_name='Title of BookMark'
    )
    runtime = models.ForeignKey(
        'workflow.Runtime',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Runtime Object',
        related_name='doc_pined_of_runtime',
    )

    def __str__(self):
        return self.title

    def before_save(self, force_insert=False):
        if force_insert is True:
            if self.runtime:
                self.title = self.runtime.doc_title
        return True

    def save(self, *args, **kwargs):
        self.before_save(
            force_insert=kwargs.get('force_insert', False),
        )
        super().save(*args, **kwargs)

        if self.runtime:
            self.runtime.doc_pined_id = self.id
            self.runtime.save(update_fields=['doc_pined_id'])

    class Meta:
        verbose_name = 'Document Pined'
        verbose_name_plural = 'Document Pined'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MailLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.CASCADE,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.CASCADE,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='This employee is performer',
        related_name='mail_log_of_employee',
    )
    mail_template = models.TextField(verbose_name='Template Using')
    mail_context = models.JSONField(verbose_name='Context Using')
    mail_html = models.TextField(verbose_name='HTML Parsed')
    mail_text = models.TextField(verbose_name='Text Parsed')
    mail_to = models.JSONField(verbose_name='Receiver')
    mail_cc = models.JSONField(verbose_name='Carbon Copy or Follower')
    mail_bcc = models.JSONField(verbose_name='Blind Carbon Copy | Blind Follower')
    mail_receiver_data = models.JSONField(
        default=dict, help_text=json.dumps({'to': [], 'cc': [], 'bcc': []}), verbose_name='As Sum Receiver Data'
    )
    mail_id = models.CharField(max_length=50, verbose_name='Mail ID Returned')
    mail_thread_id = models.CharField(max_length=50, verbose_name='Mail Thread ID Returned')
    mail_label_ids = models.JSONField(default=list, verbose_name='Mail Label IDs returned')
    is_sent = models.BooleanField(default=False, verbose_name='Flag Status Sent')

    class Meta:
        verbose_name = 'Mail Log'
        verbose_name_plural = 'Mail Log'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
