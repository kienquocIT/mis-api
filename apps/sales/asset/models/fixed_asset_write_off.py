from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel

__all__ = [
    'FixedAssetWriteOff'
]

FA_WRITE_OFF_CHOICES = [
    (0, _('Disposal or sale')),
    (1, _('Inventory adjustment')),
    (2, _('Return of leased financial assets')),
    (3, _('Convert fixed assets into instruments and tools')),
    (4, _('Capital contribution to a subsidiary')),
    (5, _('Capital contribution to a joint venture')),
    (6, _('Capital contribution to an associate company')),
]

class FixedAssetWriteOff(DataAbstractModel):
    note = models.CharField(max_length=250, blank=True, null=True)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    type = models.PositiveSmallIntegerField(choices=FA_WRITE_OFF_CHOICES, default=0)

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'FAW[n4]', True)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Fixed Asset Write Off'
        verbose_name_plural = 'Fixed Asset Write Offs'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
