# from django.db import models
#
# from apps.shared import SimpleAbstractModel
#
#
# class Indicator(SimpleAbstractModel):
#     company = models.OneToOneField(
#         'company.Company',
#         on_delete=models.CASCADE,
#         related_name='indicator_company',
#     )
#     title = models.CharField(
#         max_length=100,
#         blank=True
#     )
#     description = models.CharField(
#         max_length=200,
#         blank=True
#     )
#     order = models.IntegerField(
#         default=1
#     )
#
#     class Meta:
#         verbose_name = 'Indicator'
#         verbose_name_plural = 'Indicators'
#         ordering = ('order',)
#         default_permissions = ()
#         permissions = ()
#
#
# # SUPPORT INDICATOR
# class IndicatorFormula(SimpleAbstractModel):
#     indicator = models.ForeignKey(
#         Indicator,
#         on_delete=models.CASCADE,
#         verbose_name="indicator",
#         related_name="indicator_formula_indicator",
#     )
#
#
#
# class QuotationIndicator(SimpleAbstractModel):
#     quotation = models.ForeignKey(
#         'quotation.Quotation',
#         on_delete=models.CASCADE,
#         verbose_name="quotation",
#         related_name="quotation_indicator_quotation",
#     )
#     indicator = models.ForeignKey(
#         Indicator,
#         on_delete=models.CASCADE,
#         verbose_name="indicator",
#         related_name="quotation_indicator_indicator",
#     )
#     indicator_result = models.FloatField(
#         default=0,
#         help_text="result of specific indicator for quotation"
#     )
#     order = models.IntegerField(
#         default=1
#     )
#
#     class Meta:
#         verbose_name = 'Quotation Indicator'
#         verbose_name_plural = 'Quotation Indicators'
#         ordering = ('order',)
#         default_permissions = ()
#         permissions = ()
