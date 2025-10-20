from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


__all__ = [
    'WareHouse',
    'WarehouseEmployeeConfig',
    'WarehouseEmployeeConfigDetail',
    'WarehouseShelf'
]


class WareHouse(MasterDataAbstractModel):
    remarks = models.TextField(
        blank=True,
        verbose_name='Description of this records',
    )

    detail_address = models.CharField(blank=True, null=True, max_length=500)
    address_data = models.JSONField(default=dict)
    # {
    # country_id:
    # province_id:
    # ward_id:
    # detail_address:
    # }
    products = models.ManyToManyField(
        'saledata.Product',
        through='saledata.ProductWareHouse',
        symmetrical=False,
        blank=True,
        related_name='products_of_warehouse',
    )

    is_dropship = models.BooleanField(default=False)
    is_bin_location = models.BooleanField(default=False)
    is_virtual = models.BooleanField(default=False)
    is_pm_warehouse = models.BooleanField(default=False)

    use_for = models.SmallIntegerField(choices=[(0, _('None')), (1, _('For Equipment Loan'))], default=0)

    class Meta:
        verbose_name = 'WareHouse storage'
        verbose_name_plural = 'WareHouse storage'
        ordering = ('-code',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        number = WareHouse.objects.filter_on_company(is_delete=False).count()
        if not self.code:
            code = f"W000{str(number + 1)}"
            self.code = code
        super().save(*args, **kwargs)


class WarehouseEmployeeConfig(MasterDataAbstractModel):
    employee = models.OneToOneField('hr.Employee', on_delete=models.CASCADE, related_name='warehouse_employees_emp')
    warehouse_list = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Warehouse Employee Config'
        verbose_name_plural = 'Warehouse Employee Configs'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class WarehouseEmployeeConfigDetail(SimpleAbstractModel):
    config = models.ForeignKey(
        WarehouseEmployeeConfig,
        on_delete=models.CASCADE,
        related_name='wh_emp_config_detail_cf'
    )
    warehouse = models.ForeignKey(
        WareHouse,
        on_delete=models.CASCADE,
        related_name='wh_emp_config_detail_wh'
    )

    class Meta:
        verbose_name = 'Warehouse Employee Config Detail'
        verbose_name_plural = 'Warehouse Employee Configs Detail'
        ordering = ()
        default_permissions = ()
        permissions = ()


class WarehouseShelf(MasterDataAbstractModel):
    warehouse = models.ForeignKey(
        WareHouse,
        on_delete=models.CASCADE,
        related_name='warehouse_shelf_position_warehouse'
    )
    shelf_title = models.CharField(max_length=100)
    shelf_position = models.CharField(max_length=500)
    shelf_order = models.IntegerField(default=0)
    shelf_row = models.IntegerField(default=1)
    shelf_column = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Warehouse Shelf Position'
        verbose_name_plural = 'Warehouse Shelves Positions'
        ordering = ('shelf_order',)
        default_permissions = ()
        permissions = ()
