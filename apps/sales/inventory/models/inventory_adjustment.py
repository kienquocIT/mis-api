from django.db import models
from django.utils import timezone

from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel, IA_ITEM_ACTION_TYPE


class InventoryAdjustment(DataAbstractModel):
    warehouses_mapped = models.ManyToManyField(
        'saledata.WareHouse',
        through='InventoryAdjustmentWarehouse',
        symmetrical=False,
        blank=True,
        related_name='warehouses_mapped_ia'
    )
    employees_in_charge_mapped = models.ManyToManyField(
        'hr.Employee',
        through="InventoryAdjustmentEmployeeInCharge",
        symmetrical=False,
        blank=True,
        related_name='employees_in_charge_mapped_ia'
    )
    state = models.BooleanField(default=False)

    def update_ia_state(self):
        all_item = self.inventory_adjustment_item_mapped.all()
        done = all_item.filter(action_status=True)
        self.state = all_item.count() == done.count()
        self.save(update_fields=['state'])
        return True

    class Meta:
        verbose_name = 'Inventory Adjustment'
        verbose_name_plural = 'Inventory Adjustments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class InventoryAdjustmentWarehouse(SimpleAbstractModel):
    inventory_adjustment_mapped = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE)
    warehouse_mapped = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Inventory Adjustment Warehouse'
        verbose_name_plural = 'Inventory Adjustment Warehouses'
        ordering = ()
        default_permissions = ()
        permissions = ()


class InventoryAdjustmentEmployeeInCharge(SimpleAbstractModel):
    inventory_adjustment_mapped = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE)
    employee_mapped = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Inventory Adjustment Employee in Charge'
        verbose_name_plural = 'Inventory Adjustment Employees in Charge'
        ordering = ()
        default_permissions = ()
        permissions = ()


class InventoryAdjustmentItem(MasterDataAbstractModel):
    inventory_adjustment_mapped = models.ForeignKey(
        InventoryAdjustment,
        on_delete=models.CASCADE,
        related_name='inventory_adjustment_item_mapped'
    )
    product_warehouse = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        default=None,
    )
    product_mapped = models.ForeignKey('saledata.Product', on_delete=models.CASCADE)
    warehouse_mapped = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE)
    uom_mapped = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE)
    book_quantity = models.IntegerField()
    count = models.IntegerField()
    action_type = models.SmallIntegerField(
        choices=IA_ITEM_ACTION_TYPE,
        verbose_name='check increase, decrease or equal stock amount',
        default=0,
    )
    select_for_action = models.BooleanField(default=False)
    action_status = models.BooleanField(default=False)
    date_modified = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Inventory Adjustment Item'
        verbose_name_plural = 'Inventory Adjustment Items'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
