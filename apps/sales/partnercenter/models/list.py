from django.db import models
from django.utils import timezone

from apps.shared import SimpleAbstractModel, MasterDataAbstractModel

DATA_PROPERTY_TYPE = (
    (1, 'Text'),
    (2, 'Date time'),
    (3, 'Choices'),
    (4, 'Checkbox'),
    (5, 'Master data'),
    (6, 'Number'),
)

class List(MasterDataAbstractModel):
    data_object = models.ForeignKey(
        'partnercenter.DataObject',
        on_delete=models.CASCADE,
    )
    filter_condition = models.JSONField(default=list)
    num_of_records = models.IntegerField(default=0)
    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='partnercenter_list_employee_inherit',
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
