__all__ = [
    'ProductWareHouse',
]

from django.db import models

from apps.shared import MasterDataAbstractModel


class ProductWareHouse(MasterDataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product of WareHouse',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name='WareHouse of Product',
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='Unit Of Measure of Product',
    )
    unit_price = models.FloatField(
        default=0,
        verbose_name='Unit prices of Product',
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name='Tax of Product',
    )

    # stock
    stock_amount = models.FloatField(
        default=0,
        verbose_name="Stock",
        help_text="Stock of product",
    )
    available_amount = models.FloatField(
        default=0,
        verbose_name='Available Stock',
    )
    sold_amount = models.FloatField(
        default=0,
        verbose_name='Sold Amount',
    )

    # backup data
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product backup data',
    )
    warehouse_data = models.JSONField(
        default=dict,
        verbose_name='WareHouse backup data',
    )
    uom_data = models.JSONField(
        default=dict,
        verbose_name='Unit Of Measure backup data',
    )
    tax_data = models.JSONField(
        default=dict,
        verbose_name='Tax backup data',
    )

    @classmethod
    def push_from_receipt(
            cls,
            tenant_id,
            company_id,
            product_id,
            warehouse_id,
            uom_id,
            tax_id,
            amount: float,
            unit_price: float,
            create_when_not_found: bool = True,
            **kwargs
    ):
        if create_when_not_found:
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id, product_id=product_id, warehouse_id=warehouse_id,
                uom_id=uom_id, defaults={
                    'tax_id': tax_id,
                    'stock_amount': amount,
                    'unit_price': unit_price,
                }
            )
            if _created is True:
                return True
        else:
            try:
                obj = cls.objects.get(
                    tenant_id=tenant_id, company_id=company_id, product_id=product_id, warehouse_id=warehouse_id,
                    uom_id=uom_id
                )
            except cls.DoesNotExist:
                raise ValueError('Product not found in warehouse with UOM')
        obj.stock_amount += amount
        obj.save(update_fields=['stock_amount'])
        return True

    @classmethod
    def get_stock(
            cls,
            product_id, warehouse_id, uom_id,
            tenant_id=None, company_id=None,
    ):
        try:
            if tenant_id and company_id:
                obj = cls.objects.get(
                    product_id=product_id, warehouse_id=warehouse_id, uom_id=uom_id,
                    tenant_id=tenant_id, company_id=company_id,
                )
            else:
                obj = cls.objects.get_current(
                    product_id=product_id, warehouse_id=warehouse_id, uom_id=uom_id,
                    fill__tenant=True, fill__company=True,
                )
            return obj.stock_amount
        except cls.DoesNotExist:
            pass
        return 0

    def before_save(self, **kwargs):
        if kwargs.get('force_insert', False):
            if self.product:
                self.product_data = {
                    'id': str(self.product.id),
                    'title': str(self.product.title),
                    'code': str(self.product.code),
                }
            if self.warehouse:
                self.warehouse_data = {
                    'id': str(self.warehouse.id),
                    'title': str(self.warehouse.title),
                    'code': str(self.warehouse.code),
                }
            if self.uom:
                self.uom_data = {
                    'id': str(self.uom.id),
                    'title': str(self.uom.title),
                    'code': str(self.uom.code),
                }
            if self.tax:
                self.tax_data = {
                    'id': str(self.tax.id),
                    'title': str(self.tax.title),
                    'code': str(self.tax.code),
                    'rate': str(self.tax.rate),
                    'category_id': str(self.tax.category),
                    'type': self.tax.type,
                }
        return True

    def save(self, *args, **kwargs):
        self.before_save(**kwargs)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product mapping WareHouse'
        verbose_name_plural = 'Product mapping WareHouse'
        unique_together = ('company_id', 'warehouse_id', 'product_id', 'uom_id',)
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
