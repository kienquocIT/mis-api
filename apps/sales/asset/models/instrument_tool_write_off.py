from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = [
    'InstrumentToolWriteOff',
    'InstrumentToolWriteOffQuantity'
]

IT_WRITE_OFF_CHOICES = [
    (0, _('Disposal or sale')),
    (1, _('Inventory adjustment')),
    (2, _('Return instruments and tools to inventory'))
]

class InstrumentToolWriteOff(DataAbstractModel):
    note = models.CharField(max_length=250, blank=True, null=True)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    type = models.PositiveSmallIntegerField(choices=IT_WRITE_OFF_CHOICES, default=0)

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('instrumenttoolwriteoff', True, self, kwargs)
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Instrument Tool Write Off'
        verbose_name_plural = 'Instrument Tool Write Off List'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class InstrumentToolWriteOffQuantity(SimpleAbstractModel):
    write_off_quantity = models.IntegerField()
    instrument_tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        related_name='write_off_quantities'
    )
    instrument_tool_write_off = models.ForeignKey(
        'asset.InstrumentToolWriteOff',
        on_delete=models.CASCADE,
        related_name='quantities'
    )
