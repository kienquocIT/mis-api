from django.db import models
from apps.shared import MasterDataAbstractModel

class BiddingResultConfig(MasterDataAbstractModel):
    employee = models.ForeignKey(
        'hr.Employee',
        related_name='bidding_result_config_employee',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'BiddingResultConfig'
        verbose_name_plural = 'BiddingResultConfigs'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()