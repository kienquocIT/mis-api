from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import SimpleAbstractModel, DataAbstractModel


class EquipmentReturn(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'f5954e02-6ad1-4ebf-a4f2-0b598820f5f0'

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'ER-[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Equipment Return'
        verbose_name_plural = 'Equipments Return'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
