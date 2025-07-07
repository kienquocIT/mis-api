from django.db import models
from django.utils.translation import gettext_lazy as _
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
    state = models.SmallIntegerField(choices=[(0, _('IA Created')), (1, _('IA Working')), (2, _('IA Done'))], default=0)

    def update_ia_state(self):
        all_item_select = self.inventory_adjustment_item_mapped.filter(select_for_action=True)
        self.state = all_item_select.count() == all_item_select.filter(action_status=True).count()
        self.save(update_fields=['state'])
        return True

    class Meta:
        verbose_name = 'Inventory Adjustment'
        verbose_name_plural = 'Inventory Adjustments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if not self.code:
            self.add_auto_generate_code_to_instance(self, 'IA[n4]', False, kwargs)
        super().save(*args, **kwargs)


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
    product_mapped = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='ia_item_product_mapped'
    )
    product_mapped_data = models.JSONField(default=dict)
    warehouse_mapped = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='ia_item_warehouse_mapped'
    )
    warehouse_mapped_data = models.JSONField(default=dict)
    uom_mapped = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE)
    uom_mapped_data = models.JSONField(default=dict)
    book_quantity = models.FloatField(default=0)
    count = models.FloatField(default=0)
    issued_quantity = models.FloatField(default=0)
    receipted_quantity = models.FloatField(default=0)
    action_type = models.SmallIntegerField(
        choices=IA_ITEM_ACTION_TYPE,
        verbose_name='check increase, decrease or equal stock amount',
        default=0,
    )
    select_for_action = models.BooleanField(default=False)
    action_status = models.BooleanField(default=False)
    # goods receipt information
    gr_remain_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not goods receipted yet, update when GR finish"
    )

    class Meta:
        verbose_name = 'Inventory Adjustment Item'
        verbose_name_plural = 'Inventory Adjustment Items'
        ordering = ('product_mapped__code',)
        default_permissions = ()
        permissions = ()


class IAItemBeingAdjusted(SimpleAbstractModel):
    ia_mapped = models.ForeignKey(
        InventoryAdjustment,
        on_delete=models.CASCADE,
        related_name='ia_mapped_being_adjusted'
    )
    product_mapped = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='product_mapped_being_adjusted'
    )
    warehouse_mapped = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_mapped_being_adjusted'
    )
