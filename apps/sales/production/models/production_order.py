from django.db import models

from apps.shared import DataAbstractModel


class ProductionOrder(DataAbstractModel):
    bom = models.ForeignKey(
        'production.BOM',
        on_delete=models.CASCADE,
        verbose_name="bom",
        related_name="production_order_bom",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="production_order_product",
    )
    quantity = models.FloatField(default=0, help_text='quantity order')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom",
        related_name="production_order_uom",
        null=True,
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="production_order_warehouse",
        null=True,
    )
    date_start = models.DateField(null=True)
    date_end = models.DateField(null=True)
    group = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="group",
        related_name="production_order_group",
        null=True,
    )
    time = models.FloatField(default=0, help_text='total time for production')

    class Meta:
        verbose_name = 'Production order'
        verbose_name_plural = 'Production orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("PO")[1])
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
            code = 'PO0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'PO{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            instance.code = cls.generate_code(company_id=instance.company_id)
            kwargs['update_fields'].append('code')
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    # code
                    self.push_code(instance=self, kwargs=kwargs)
        # hit DB
        super().save(*args, **kwargs)
