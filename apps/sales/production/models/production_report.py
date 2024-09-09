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
    quantity = models.FloatField(default=0, help_text='quantity from production order')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="production_report_uom",
        null=True,
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="production_report_warehouse",
        null=True,
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    quantity_finished = models.FloatField(default=0, help_text='quantity finished')
    quantity_ng = models.FloatField(default=0, help_text='quantity not good')
    task_data = models.JSONField(default=list, help_text='data json of task, records in ProductionReportTask')

    class Meta:
        verbose_name = 'Production report'
        verbose_name_plural = 'Production reports'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("PR")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'PR0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'PR{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance):
        if not instance.code:
            instance.code = cls.generate_code(company_id=instance.company_id)
        return True

    def save(self, *args, **kwargs):
        self.push_code(instance=self)
        # hit DB
        super().save(*args, **kwargs)


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
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Production Report Task'
        verbose_name_plural = 'Production Report Tasks'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
