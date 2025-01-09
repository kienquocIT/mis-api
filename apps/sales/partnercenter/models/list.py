from django.db import models
from django.utils import timezone

from apps.shared import SimpleAbstractModel

DATA_PROPERTY_TYPE = (
    (1, 'Text'),
    (2, 'Date time'),
    (3, 'Choices'),
    (4, 'Checkbox'),
    (5, 'Master data'),
    (6, 'Number'),
)

class List(SimpleAbstractModel):
    title = models.CharField(max_length=100)
    data_object = models.ForeignKey(
        'partnercenter.DataObject',
        on_delete=models.CASCADE,
    )
    filter_condition = models.JSONField(default=list)
    num_of_records = models.IntegerField(default=0)
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
    )
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='partnercenter_list_belong_to_tenant',
    )
    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='partnercenter_list_employee_inherit',
    )
    employee_created = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='Employee created this record',
        related_name='partnercenter_list_employee_creator',
    )

    class Meta:
        verbose_name = 'Partner List'
        verbose_name_plural = 'Partner Lists'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

class DataObject(SimpleAbstractModel):
    title = models.CharField(max_length=100)
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        null=True
    )
