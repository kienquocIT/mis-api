__all__ = [
    'ProductWareHouse',
    'ProductWareHouseLot',
    'ProductWareHouseSerial',
]
from django.db import models

from apps.shared import MasterDataAbstractModel
from .product import UnitOfMeasure


class ProductWareHouse(MasterDataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product of WareHouse',
        related_name='product_warehouse_product'
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
        null=True,
    )
    unit_price = models.FloatField(
        default=0,
        verbose_name='Unit prices of Product',
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name='Tax of Product',
        null=True,
    )

    # stock
    stock_amount = models.FloatField(
        default=0,
        verbose_name="Stock",
        help_text="Physical amount product in warehouse, =(receipt_amount - sold_amount)",
    )
    receipt_amount = models.FloatField(
        default=0,
        verbose_name='Receipt Amount',
        help_text='Amount product receipted, update when goods receipt'
    )
    sold_amount = models.FloatField(
        default=0,
        verbose_name='Sold Amount',
        help_text='Amount product delivered, update when deliver'
    )
    picked_ready = models.FloatField(
        default=0,
        verbose_name='Picked Amount',
    )
    used_amount = models.FloatField(
        default=0,
        verbose_name='Used Amount',
        help_text='Amount product delivered for employee use'
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
            lot_data=None,
            serial_data=None,
            **kwargs
    ):
        if create_when_not_found:
            obj, _created = cls.objects.get_or_create(
                tenant_id=tenant_id, company_id=company_id, product_id=product_id, warehouse_id=warehouse_id,
                uom_id=uom_id, defaults={
                    'tax_id': tax_id,
                    'stock_amount': amount,
                    'receipt_amount': amount,
                    'unit_price': unit_price,
                }
            )
            if _created is True:
                if lot_data and isinstance(lot_data, list):
                    ProductWareHouseLot.create(
                        tenant_id=tenant_id,
                        company_id=company_id,
                        product_warehouse_id=obj.id,
                        lot_data=lot_data
                    )
                if serial_data and isinstance(serial_data, list):
                    ProductWareHouseSerial.create(
                        tenant_id=tenant_id,
                        company_id=company_id,
                        product_warehouse_id=obj.id,
                        serial_data=serial_data
                    )
                return True
        else:
            try:
                obj = cls.objects.get(
                    tenant_id=tenant_id, company_id=company_id, product_id=product_id, warehouse_id=warehouse_id,
                )
            except cls.DoesNotExist:
                raise ValueError('Product not found in warehouse with UOM')
        obj.receipt_amount += amount
        obj.stock_amount = obj.receipt_amount - obj.sold_amount
        if lot_data and isinstance(lot_data, list):
            ProductWareHouseLot.create(
                tenant_id=tenant_id,
                company_id=company_id,
                product_warehouse_id=obj.id,
                lot_data=lot_data
            )
        if serial_data and isinstance(serial_data, list):
            ProductWareHouseSerial.create(
                tenant_id=tenant_id,
                company_id=company_id,
                product_warehouse_id=obj.id,
                serial_data=serial_data
            )
        obj.save(update_fields=['stock_amount', 'receipt_amount'])
        return True

    @classmethod
    def get_stock(
            cls,
            product_id, warehouse_id, uom_id,
            tenant_id=None, company_id=None,
    ):
        try:
            uom = UnitOfMeasure.objects.get(id=uom_id)
            uom_ratio = uom.ratio
            if tenant_id and company_id:
                objs = cls.objects.filter(
                    product_id=product_id, warehouse_id=warehouse_id,
                    tenant_id=tenant_id, company_id=company_id,
                )
            else:
                objs = cls.objects.filter_current(
                    product_id=product_id, warehouse_id=warehouse_id,
                    fill__tenant=True, fill__company=True,
                )
            count = 0
            for obj in objs:
                count += ((obj.stock_amount - obj.sold_amount) * obj.uom.ratio) / uom_ratio
            count = round(count, uom.rounding)
            return count
        except cls.DoesNotExist:
            pass
        return 0

    @classmethod
    def get_picked_ready(
            cls,
            product_id, warehouse_id, uom_id,
            tenant_id=None, company_id=None,
    ):
        try:
            uom = UnitOfMeasure.objects.get(id=uom_id)
            uom_ratio = uom.ratio
            if tenant_id and company_id:
                objs = cls.objects.filter(
                    product_id=product_id, warehouse_id=warehouse_id,
                    tenant_id=tenant_id, company_id=company_id,
                )
            else:
                objs = cls.objects.filter_current(
                    product_id=product_id, warehouse_id=warehouse_id,
                    fill__tenant=True, fill__company=True,
                )
            count = 0
            for obj in objs:
                count += (obj.picked_ready * obj.uom.ratio) / uom_ratio
            count = round(count, uom.rounding)
            return count
        except cls.DoesNotExist:
            pass
        return 0

    @classmethod
    def pop_from_transfer(cls, instance_id, amount):
        try:
            obj = cls.objects.get(id=instance_id)
        except cls.DoesNotExist:
            raise ValueError('Product not found in warehouse with UOM')
        obj.stock_amount -= amount
        obj.product.stock_amount -= amount
        obj.product.available_amount -= amount
        obj.save(update_fields=['stock_amount'])
        obj.product.save(update_fields=['stock_amount', 'available_amount'])
        return True

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
                    'type': self.tax.tax_type,
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


# class ProductWareHousePeriod(MasterDataAbstractModel):
#     product_warehouse = models.ForeignKey(
#         ProductWareHouse,
#         on_delete=models.CASCADE,
#         verbose_name='Product WareHouse related',
#     )
#     opening_balance = models.FloatField()
#     purchase_amount = models.FloatField()
#     bought_amount = models.FloatField()
#
#     year = models.PositiveSmallIntegerField()
#     order = models.PositiveSmallIntegerField()
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#
#     class Meta:
#         verbose_name = 'Product at WareHouse in Period'
#         verbose_name_plural = 'Product at WareHouse in Period'
#         ordering = ('-date_created',)
#         default_permissions = ()
#         permissions = ()


class ProductWareHouseLot(MasterDataAbstractModel):
    product_warehouse = models.ForeignKey(
        ProductWareHouse,
        on_delete=models.CASCADE,
        verbose_name="product warehouse",
        related_name="product_warehouse_lot_product_warehouse",
    )
    lot_number = models.CharField(max_length=100, blank=True, null=True)
    quantity_import = models.FloatField(default=0)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Product Warehouse Lot'
        verbose_name_plural = 'Product Warehouse Lots'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            tenant_id,
            company_id,
            product_warehouse_id,
            lot_data,
    ):
        cls.objects.bulk_create([cls(
            **data,
            tenant_id=tenant_id,
            company_id=company_id,
            product_warehouse_id=product_warehouse_id,
        ) for data in lot_data])
        return True


class ProductWareHouseSerial(MasterDataAbstractModel):
    product_warehouse = models.ForeignKey(
        ProductWareHouse,
        on_delete=models.CASCADE,
        verbose_name="product warehouse",
        related_name="product_warehouse_serial_product_warehouse",
    )
    vendor_serial_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)
    warranty_start = models.DateTimeField(null=True)
    warranty_end = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Product Warehouse Serial'
        verbose_name_plural = 'Product Warehouse Serials'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def create(
            cls,
            tenant_id,
            company_id,
            product_warehouse_id,
            serial_data
    ):
        cls.objects.bulk_create([cls(
            **data,
            tenant_id=tenant_id,
            company_id=company_id,
            product_warehouse_id=product_warehouse_id,
        ) for data in serial_data])
        return True
