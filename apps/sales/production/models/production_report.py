from django.db import models

from apps.shared import DataAbstractModel, MasterDataAbstractModel


class ProductionReport(DataAbstractModel):
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        verbose_name="production order",
        related_name="production_report_production_order",
    )
    production_order_data = models.JSONField(default=dict, help_text='data json of production order')
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="production_report_product",
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    quantity = models.FloatField(default=0, help_text='quantity order')
    quantity_finished = models.FloatField(default=0, help_text='quantity finished')
    quantity_ng = models.FloatField(default=0, help_text='quantity not good')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="production_report_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')

    class Meta:
        verbose_name = 'Production report'
        verbose_name_plural = 'Production reports'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductionReportTask(MasterDataAbstractModel):
    production_report = models.ForeignKey(
        'production.ProductionReport',
        on_delete=models.CASCADE,
        verbose_name="production report",
        related_name="pr_task_production_report",
    )
    is_task = models.BooleanField(default=False, help_text='flag to know this record is task')
    task_title = models.CharField(max_length=100, blank=True)
    task_order = models.IntegerField(default=1)
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="pr_task_product",
        null=True,
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="pr_task_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    quantity = models.FloatField(default=0)
    quantity_actual = models.FloatField(default=0)
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="pr_task_warehouse",
        null=True,
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Production Report Task'
        verbose_name_plural = 'Production Report Tasks'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
