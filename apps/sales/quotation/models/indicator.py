from django.db import models

from apps.shared import SimpleAbstractModel


# class ParamSale(SimpleAbstractModel):
#     application_code = models.CharField(
#         max_length=100,
#         blank=True
#     )
#     title = models.CharField(
#         max_length=100,
#         blank=True
#     )
#     code = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="field name in model or id of element define this field in html"
#     )
#
#     class Meta:
#         verbose_name = 'Param Sale'
#         verbose_name_plural = 'Param Sales'
#         default_permissions = ()
#         permissions = ()


class Indicator(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='indicator_company',
    )
    title = models.CharField(
        max_length=100,
        blank=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    application_code = models.CharField(
        max_length=100,
        blank=True
    )
    is_indicator_param = models.BooleanField(default=False)
    is_sale_param = models.BooleanField(default=False)
    is_math_operator = models.BooleanField(default=False)
    formula_indicator_params = models.JSONField(
        default=list,
        help_text="setup by indicator params, examples: ['indicatorID1', '-', 'indicatorID2', '+', 'indicatorID3',...]"
    )
    formula_sale_params = models.JSONField(
        default=list,
        help_text="setup by sale params, examples: ['saleID1', '-', 'saleID2', '+', 'saleID3',...]"
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Indicator'
        verbose_name_plural = 'Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


# SUPPORT INDICATOR
# class IndicatorFormula(SimpleAbstractModel):
#     indicator = models.ForeignKey(
#         Indicator,
#         on_delete=models.CASCADE,
#         verbose_name="indicator",
#         related_name="indicator_formula_indicator",
#     )
#     indicator_param = models.ForeignKey(
#         Indicator,
#         on_delete=models.CASCADE,
#         verbose_name="indicator",
#         related_name="indicator_formula_indicator_param",
#         null=True
#     )
#     sale_param = models.ForeignKey(
#         ParamSale,
#         on_delete=models.CASCADE,
#         verbose_name="sale params",
#         related_name="indicator_formula_quotation_param",
#         help_text="params of application, defined in model ParamSale, filter by application_code",
#         null=True
#     )
#     math_operator = models.CharField(
#         max_length=10,
#         blank=True
#     )
#     order = models.IntegerField(
#         default=1
#     )
#
#     class Meta:
#         verbose_name = 'Indicator Formula'
#         verbose_name_plural = 'Indicator Formulas'
#         ordering = ('order',)
#         default_permissions = ()
#         permissions = ()


class QuotationIndicator(SimpleAbstractModel):
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_indicator_quotation",
    )
    indicator = models.ForeignKey(
        Indicator,
        on_delete=models.CASCADE,
        verbose_name="indicator",
        related_name="quotation_indicator_indicator",
    )
    indicator_result = models.FloatField(
        default=0,
        help_text="result of specific indicator for quotation"
    )
    indicator_rate_result = models.FloatField(
        default=0,
        help_text="rate result of specific indicator for quotation"
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Indicator'
        verbose_name_plural = 'Quotation Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
