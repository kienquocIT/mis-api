from django.db import models
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


class BiddingResultConfig(MasterDataAbstractModel):
    employee = models.JSONField(
        default=list,
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name = 'BiddingResultConfig'
        verbose_name_plural = 'BiddingResultConfigs'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

class BiddingResultConfigEmployee(SimpleAbstractModel):
    bidding_result_config = models.ForeignKey(
        "saledata.BiddingResultConfig",
        on_delete=models.CASCADE,
        verbose_name="bidding result config",
        related_name="bidding_result_config_employee_bid_config"
    )

    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,
        verbose_name="employee",
        related_name="bidding_result_config_employee_employee"
    )

    class Meta:
        verbose_name = 'BiddingResultConfigEmployee'
        verbose_name_plural = 'BiddingResultConfigEmployeeList'
        ordering = ()
        default_permissions = ()
        permissions = ()