from django.db import models

from apps.shared import DataAbstractModel


class Opportunity(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="opportunity_customer",
        null=True
    )

    class Meta:
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
