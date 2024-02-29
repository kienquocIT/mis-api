from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods
from apps.shared import DataAbstractModel, SimpleAbstractModel


class ReportInventory(DataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_inventory_product',
    )

    period_mapped = models.ForeignKey(
        'saledata.Periods',
        on_delete=models.CASCADE,
        related_name='report_inventory_period',
        null=True,
    )
    sub_period_order = models.IntegerField()

    @classmethod
    def create_report_inventory_item(cls, product_obj, period_mapped, sub_period_order):
        obj = cls.objects.create(
            tenant_id=product_obj.tenant_id,
            company_id=product_obj.company_id,
            employee_created_id=product_obj.employee_created_id,
            employee_inherit_id=product_obj.employee_inherit_id,
            product=product_obj,
            period_mapped=period_mapped,
            sub_period_order=sub_period_order
        )
        return obj

    class Meta:
        verbose_name = 'Report Inventory'
        verbose_name_plural = 'Report Inventories'
        ordering = ('sub_period_order',)
        default_permissions = ()
        permissions = ()


class ReportInventorySub(DataAbstractModel):
    report_inventory = models.ForeignKey(
        ReportInventory,
        on_delete=models.CASCADE,
        related_name='report_inventory_by_month',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_inventory_by_month_product'
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_inventory_by_month_warehouse',
        null=True
    )

    system_date = models.DateTimeField(null=True)
    posting_date = models.DateTimeField(null=True)
    document_date = models.DateTimeField(null=True)

    stock_type = models.SmallIntegerField(choices=[(1, 'In'), (-1, 'Out')])
    trans_id = models.CharField(blank=True, max_length=100, null=True)
    trans_code = models.CharField(blank=True, max_length=100, null=True)
    trans_title = models.CharField(blank=True, max_length=100, null=True)

    quantity = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    value = models.FloatField(default=0)

    current_quantity = models.FloatField(default=0)
    current_cost = models.FloatField(default=0)
    current_value = models.FloatField(default=0)

    @classmethod
    def create_new_log(cls, activities_data, period_mapped, sub_period_order):
        """
            Lặp từng sản phẩm được nhập - xuất:
            B1: Get ReportInventory object theo sp+sub_period_order
            Nếu có:
            + Tạo log
            Nếu không:
            + Tạo ReportInventory object theo sp+sub_period_order
            + Tạo log
        """
        bulk_info = []
        for item in activities_data:
            report_inventory_obj = ReportInventory.objects.filter(
                product=item['product'],
                sub_period_order=sub_period_order - period_mapped.space_month
            ).first()
            if not report_inventory_obj:
                report_inventory_obj = ReportInventory.create_report_inventory_item(
                    product_obj=item['product'],
                    period_mapped=period_mapped,
                    sub_period_order=sub_period_order - period_mapped.space_month
                )

            new_log = cls(
                report_inventory=report_inventory_obj,
                product=item['product'],
                warehouse=item['warehouse'],
                system_date=item['system_date'],
                posting_date=item['posting_date'],
                document_date=item['document_date'],
                stock_type=item['stock_type'],
                trans_id=item['trans_id'],
                trans_code=item['trans_code'],
                trans_title=item['trans_title'],
                quantity=item['quantity'],
                cost=item['cost'],
                value=item['value']
            )
            bulk_info.append(new_log)
        new_logs = cls.objects.bulk_create(bulk_info)

        return new_logs

    @classmethod
    def logging_when_stock_activities_happened(cls, activities_obj_date, activities_data):
        period_mapped = Periods.objects.filter_current(
            fill__company=True,
            fill__tenant=True,
            fiscal_year=activities_obj_date.year
        ).first()
        if period_mapped:
            new_logs = cls.create_new_log(activities_data, period_mapped, activities_obj_date.month)
            for log in new_logs:
                obj_by_warehouse = ReportInventoryProductWarehouse.objects.filter(
                    product=log.product,
                    warehouse=log.warehouse,
                    period_mapped=period_mapped,
                    sub_period_order=activities_obj_date.month - period_mapped.space_month
                ).first()
                if not obj_by_warehouse:
                    obj_by_warehouse = ReportInventoryProductWarehouse.objects.create(
                        product=log.product,
                        warehouse=log.warehouse,
                        period_mapped=period_mapped,
                        sub_period_order=activities_obj_date.month - period_mapped.space_month
                    )

                if log.stock_type == 1:
                    new_quantity = obj_by_warehouse.ending_balance_quantity + log.quantity
                    sum_value = obj_by_warehouse.ending_balance_value + log.value
                    new_cost = sum_value / new_quantity
                    new_value = new_cost * new_quantity
                else:
                    new_quantity = obj_by_warehouse.ending_balance_quantity - log.quantity
                    new_cost = obj_by_warehouse.ending_balance_cost
                    new_value = new_cost * new_quantity

                log.current_quantity = new_quantity
                log.current_cost = new_cost
                log.current_value = new_value
                log.save(
                    update_fields=['current_quantity', 'current_cost', 'current_value']
                )

                obj_by_warehouse.ending_balance_quantity = new_quantity
                obj_by_warehouse.ending_balance_cost = new_cost
                obj_by_warehouse.ending_balance_value = new_value
                obj_by_warehouse.save(
                    update_fields=['ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value']
                )
            return True
        raise serializers.ValidationError(
            {'Period missing': f'Period of fiscal year {activities_obj_date.year} does not exist.'}
        )

    class Meta:
        verbose_name = 'Report Inventory By Month'
        verbose_name_plural = 'Report Inventory By Months'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ReportInventoryProductWarehouse(SimpleAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_inventory_product_warehouse_product',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_inventory_product_warehouse_warehouse',
        null=True
    )
    period_mapped = models.ForeignKey(
        'saledata.Periods',
        on_delete=models.CASCADE,
        related_name='report_inventory_product_warehouse_period',
        null=True,
    )
    sub_period_order = models.IntegerField()

    opening_balance_quantity = models.FloatField(default=0)
    opening_balance_cost = models.FloatField(default=0)
    opening_balance_value = models.FloatField(default=0)

    ending_balance_quantity = models.FloatField(default=0)
    ending_balance_cost = models.FloatField(default=0)
    ending_balance_value = models.FloatField(default=0)

    for_balance = models.BooleanField(default=False)
    wrong_cost = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Report Inventory Product Warehouse'
        verbose_name_plural = 'Report Inventories Product Warehouse'
        ordering = ()
        default_permissions = ()
        permissions = ()
