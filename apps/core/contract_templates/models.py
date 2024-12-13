from django.db import models

from apps.shared import MasterDataAbstractModel


class ContractTemplate(MasterDataAbstractModel):
    template = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Contract template'
        verbose_name_plural = 'Contract'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
