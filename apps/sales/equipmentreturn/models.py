from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel


class EquipmentReturn(DataAbstractModel):
    account_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    account_mapped_data = models.JSONField(default=dict)
    document_date = models.DateTimeField(null=True)

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'f5954e02-6ad1-4ebf-a4f2-0b598820f5f0'

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('equipmentreturn', True, self, kwargs)
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Equipment Return'
        verbose_name_plural = 'Equipments Return'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
