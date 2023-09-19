from django.db import models
from apps.shared import DataAbstractModel, SimpleAbstractModel


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

    class Meta:
        verbose_name = 'Inventory Adjustment'
        verbose_name_plural = 'Inventory Adjustments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class InventoryAdjustmentWarehouse(SimpleAbstractModel):
    inventory_adjustment_mapped = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE)
    warehouse_mapped = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE)


class InventoryAdjustmentEmployeeInCharge(SimpleAbstractModel):
    inventory_adjustment_mapped = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE)
    employee_mapped = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)


class InventoryAdjustmentItem(SimpleAbstractModel):
    inventory_adjustment_mapped = models.ForeignKey(
        InventoryAdjustment,
        on_delete=models.CASCADE,
        related_name='inventory_adjustment_item_mapped'
    )
    product_mapped = models.ForeignKey('saledata.Product', on_delete=models.CASCADE)
    warehouse_mapped = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE)
    uom_mapped = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE)
    book_quantity = models.IntegerField()
    count = models.IntegerField()
    select_for_action = models.BooleanField(default=False)
    action_status = models.BooleanField(default=False)
