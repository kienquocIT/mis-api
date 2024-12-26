import json

from django.db import models

from apps.shared import MasterDataAbstractModel


class ContractTemplate(MasterDataAbstractModel):
    template = models.TextField(blank=True)
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        related_name='contract_template_map_app'
    )

    class Meta:
        verbose_name = 'Contract template list'
        verbose_name_plural = 'get contract template list'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
