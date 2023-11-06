from django.db import models

from apps.shared import DataAbstractModel


class ReportRevenue(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="report_revenue_sale_order",
    )
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='report_revenue_group_inherit',
    )
    date_approved = models.DateTimeField(
        null=True,
        help_text='date at the time sale order approved in WF',
    )

    class Meta:
        verbose_name = 'Report Revenue'
        verbose_name_plural = 'Report Revenues'
        ordering = ('employee_inherit__code',)
        default_permissions = ()
        permissions = ()
