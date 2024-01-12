from django.db import models
from apps.shared import MasterDataAbstractModel


class Periods(MasterDataAbstractModel):
    fiscal_year = models.IntegerField(null=False)
    start_date = models.DateField(null=False)

    class Meta:
        verbose_name = 'Periods'
        verbose_name_plural = 'Periods'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
