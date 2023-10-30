from django.db import models

from apps.shared import MasterDataAbstractModel


class SaleOrderIndicatorConfig(MasterDataAbstractModel):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sale_order_indicator_config_company',
    )
    title = models.CharField(
        max_length=100,
        blank=True
    )
    remark = models.CharField(
        max_length=200,
        blank=True
    )
    example = models.CharField(
        max_length=300,
        blank=True
    )
    application_code = models.CharField(
        max_length=100,
        blank=True
    )
    formula_data = models.JSONField(default=list)
    formula_data_show = models.TextField(
        blank=True,
        null=True
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Sale Order Indicator Config'
        verbose_name_plural = 'Sale Order Indicator Configs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class SaleOrderIndicator(MasterDataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="sale_order_indicator_sale_order",
    )
    indicator = models.ForeignKey(
        SaleOrderIndicatorConfig,
        on_delete=models.CASCADE,
        verbose_name="indicator",
        related_name="sale_order_indicator_indicator",
        null=True
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
        related_name="sale_order_indicator_quotation_indicator",
        null=True
    )
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
        verbose_name = 'Sale Order Indicator'
        verbose_name_plural = 'Sale Order Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
