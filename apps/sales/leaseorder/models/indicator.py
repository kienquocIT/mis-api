from django.db import models

from apps.shared import MasterDataAbstractModel


class LeaseOrderIndicator(MasterDataAbstractModel):
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="lease_order_indicator_lease_order",
    )
    indicator_value = models.FloatField(
        default=0,
        help_text="value of specific indicator for sale order"
    )
    indicator_rate = models.FloatField(
        default=0,
        help_text="rate value of specific indicator for sale order"
    )
    quotation_indicator = models.ForeignKey(
        'quotation.QuotationIndicatorConfig',
        on_delete=models.CASCADE,
        verbose_name="quotation indicator",
        related_name="lease_order_indicator_quotation_indicator",
        null=True
    )
    quotation_indicator_data = models.JSONField(default=dict, help_text='data json of quotation indicator')
    quotation_indicator_value = models.FloatField(
        default=0,
        help_text="value of specific indicator for quotation mapped with sale order"
    )
    quotation_indicator_rate = models.FloatField(
        default=0,
        help_text="rate value of specific indicator for quotation mapped with sale order"
    )
    difference_indicator_value = models.FloatField(
        default=0,
        help_text="difference value between quotation and sale order"
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Lease Order Indicator'
        verbose_name_plural = 'Lease Order Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
