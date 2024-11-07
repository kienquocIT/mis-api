from django.db import models
from django.utils import timezone

from apps.shared import MasterDataAbstractModel


class EmployeeContract(MasterDataAbstractModel):
    effected_date = models.DateTimeField(
        verbose_name='Start date',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Employee contract'
        verbose_name_plural = 'Employee contract'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
