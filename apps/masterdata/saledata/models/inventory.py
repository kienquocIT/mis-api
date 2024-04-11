from django.db import models
from rest_framework import serializers
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel, WAREHOUSE_TYPE

__all__ = [
    'WareHouse',
    'WarehouseEmployeeConfig',
    'WarehouseEmployeeConfigDetail'
]


class WareHouse(MasterDataAbstractModel):
    remarks = models.TextField(
        blank=True,
        verbose_name='Description of this records',
    )

    city = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_city'
    )

    district = models.ForeignKey(
        'base.District',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_district'
    )

    ward = models.ForeignKey(
        'base.Ward',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_ward'
    )

    address = models.CharField(
        max_length=500,
        default='',
        blank=True
    )
    full_address = models.CharField(
        max_length=1000,
        default='',
        blank=True
    )

    agency = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_agency'
    )

    warehouse_type = models.SmallIntegerField(
        choices=WAREHOUSE_TYPE,
        default=0,
    )

    products = models.ManyToManyField(
        'saledata.Product',
        through='saledata.ProductWareHouse',
        symmetrical=False,
        blank=True,
        related_name='products_of_warehouse',
    )
    is_dropship = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'WareHouse storage'
        verbose_name_plural = 'WareHouse storage'
        ordering = ()
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_interact_warehouse(cls, employee_obj, warehouse_id):
        interact = WarehouseEmployeeConfig.objects.filter(employee=employee_obj).first()
        if interact:
            if warehouse_id not in interact.warehouse_list:
                raise serializers.ValidationError({"Error": 'You are not allowed to interact with this warehouse.'})
        return True

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        warehouse = WareHouse.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
        ).count()
        char = "W"
        if not self.code:
            temper = "%04d" % (warehouse + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code
        super().save(*args, **kwargs)


class WarehouseEmployeeConfig(MasterDataAbstractModel):
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='warehouse_employees_emp')
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
