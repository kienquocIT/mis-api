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

class Property(SimpleAbstractModel):
    title = models.CharField(max_length=100, blank=True)
    field_code = models.CharField(max_length=100, help_text='Name of the model field')
    type = models.SmallIntegerField(choices=DATA_PROPERTY_TYPE)

class DataObject(SimpleAbstractModel):
    title = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, help_text='Name of the model, e.g: Account, Contact ...')
    app_name = models.CharField(max_length=100,  help_text='Name of the app folder, e.g: opportunity, cashoutflow')
