from django.db import models
from rest_framework import serializers
from apps.shared import DataAbstractModel


class ReportInventory(DataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_inventory_product',
    )

    order = models.IntegerField()

    stock_quantity = models.FloatField(default=0)
    stock_unit_price = models.FloatField(default=0)
    stock_subtotal_price = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Report Inventory'
        verbose_name_plural = 'Report Inventories'
        ordering = ('order',)
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

    quantity = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    value = models.FloatField(default=0)

    current_quantity = models.FloatField(default=0)
    current_unit_price = models.FloatField(default=0)
    current_subtotal_price = models.FloatField(default=0)

    @classmethod
    def new_log_when_stock_activities_happened(cls, activities_obj_date, activities_data):
        sub_period = activities_obj_date.month
        # lọc các item của sub_period đó
        report_inventory_ft = ReportInventory.objects.filter(order=sub_period)
        if report_inventory_ft.exists():
            bulk_info = []
            for item in activities_data:
                # lọc các item có product=item.product
                report_inventory_obj = report_inventory_ft.filter(product=item['product']).first()
                if report_inventory_obj:
                    cost_cal = item['cost'] if item['stock_type'] == 1 else report_inventory_obj.stock_unit_price
                    value_cal = item['value'] if item['stock_type'] == 1 else cost_cal * item['quantity']
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
                        quantity=item['quantity'],
                        cost=cost_cal,
                        value=value_cal
                    )
                    bulk_info.append(new_log)
            cls.objects.bulk_create(bulk_info)

            for info in bulk_info:
                report_inventory_obj = info.report_inventory

                if info.stock_type == 1:
                    new_quantity = report_inventory_obj.stock_quantity + info.quantity
                    sum_subtotal_price = report_inventory_obj.stock_subtotal_price + info.value
                    new_unit_price = sum_subtotal_price / new_quantity
                    new_subtotal_price = new_unit_price * new_quantity
                else:
                    new_quantity = report_inventory_obj.stock_quantity - info.quantity
                    new_unit_price = info.cost
                    new_subtotal_price = new_unit_price * new_quantity

                report_inventory_obj.stock_quantity = new_quantity
                report_inventory_obj.stock_unit_price = new_unit_price
                report_inventory_obj.stock_subtotal_price = new_subtotal_price
                report_inventory_obj.save(update_fields=[
                    'stock_quantity', 'stock_unit_price', 'stock_subtotal_price'
                ])

                info.current_quantity = new_quantity
                info.current_unit_price = new_unit_price
                info.current_subtotal_price = new_subtotal_price
                info.save(update_fields=[
                    'current_quantity', 'current_unit_price', 'current_subtotal_price'
                ])
            return True
        raise serializers.ValidationError({'Sub period error': 'Dont have any sub period'})

    class Meta:
        verbose_name = 'Report Inventory By Month'
        verbose_name_plural = 'Report Inventory By Months'
        ordering = ()
        default_permissions = ()
        permissions = ()
