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
    list_result = models.JSONField(default=list)
    num_of_records = models.IntegerField(default=0)
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
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
    )
