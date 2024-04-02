from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods
from apps.shared import DataAbstractModel


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
    sub_period = models.ForeignKey(
        'saledata.SubPeriods',
        on_delete=models.CASCADE,
        related_name='report_inventory_product_sub_period',
        null=True,
    )

    @classmethod
    def create_report_inventory_item(cls, product_obj, period_mapped, sub_period_order):
        obj = cls.objects.create(
            tenant_id=product_obj.tenant_id,
            company_id=product_obj.company_id,
            employee_created_id=product_obj.employee_created_id,
            employee_inherit_id=product_obj.employee_inherit_id,
            product=product_obj,
            period_mapped=period_mapped,
            sub_period_order=sub_period_order,
            sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        )
        return obj

    class Meta:
        verbose_name = 'Report Inventory'
        verbose_name_plural = 'Report Inventories'
        ordering = ('product__code',)
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

    lot_data = models.JSONField(default=list)

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
                tenant_id=period_mapped.tenant_id,
                company_id=period_mapped.company_id,
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
                value=item['value'],
                lot_data=item.get('lot_data', [])
            )
            bulk_info.append(new_log)
        new_logs = cls.objects.bulk_create(bulk_info)

        return new_logs, [obj.pk for obj in new_logs]

    @classmethod
    def process_in_each_log(cls, log, new_logs_id_list, period_mapped, sub_period_order):
        sub_list = ReportInventorySub.objects.filter(
            product=log.product,
            warehouse=log.warehouse,
            # report_inventory__period_mapped=period_mapped,
            # report_inventory__sub_period_order=sub_period_order
        ).exclude(id__in=new_logs_id_list)
        latest_trans = sub_list.latest('date_created') if sub_list.count() > 0 else None
        if not latest_trans:
            now_ending_balance_quantity = 0
            now_ending_balance_cost = 0
            now_ending_balance_value = 0
        else:
            now_ending_balance_quantity = latest_trans.current_quantity
            now_ending_balance_cost = latest_trans.current_cost
            now_ending_balance_value = latest_trans.current_value

        prd_wh_this_sub = ReportInventoryProductWarehouse.objects.filter(
            tenant_id=period_mapped.tenant_id,
            company_id=period_mapped.company_id,
            product=log.product,
            warehouse=log.warehouse,
            period_mapped=period_mapped,
            sub_period_order=sub_period_order,
            sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        )
        if not prd_wh_this_sub.exists():
            ReportInventoryProductWarehouse.objects.create(
                tenant_id=period_mapped.tenant_id,
                company_id=period_mapped.company_id,
                product=log.product,
                warehouse=log.warehouse,
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                opening_balance_quantity=now_ending_balance_quantity,
                opening_balance_cost=now_ending_balance_cost,
                opening_balance_value=now_ending_balance_value
            )

        if log.stock_type == 1:
            new_quantity = now_ending_balance_quantity + log.quantity
            sum_value = now_ending_balance_value + log.value
            new_cost = sum_value / new_quantity
            new_value = sum_value
        else:
            new_quantity = now_ending_balance_quantity - log.quantity
            new_cost = now_ending_balance_cost
            new_value = new_cost * new_quantity

        log.current_quantity = new_quantity
        log.current_cost = new_cost
        log.current_value = new_value
        log.save(
            update_fields=['current_quantity', 'current_cost', 'current_value']
        )
        return log

    @classmethod
    def logging_when_stock_activities_happened(cls, activities_obj, activities_obj_date, activities_data):
        period_mapped = Periods.objects.filter(
            tenant_id=activities_obj.tenant_id,
            company_id=activities_obj.company_id,
            fiscal_year=activities_obj_date.year
        ).first()
        sub_period_order = activities_obj_date.month - period_mapped.space_month
        if period_mapped:
            new_logs, new_logs_id_list = cls.create_new_log(activities_data, period_mapped, activities_obj_date.month)
            for log in new_logs:
                log_return = cls.process_in_each_log(log, new_logs_id_list, period_mapped, sub_period_order)
                new_logs_id_list = [log_id for log_id in new_logs_id_list if log_id != log_return.id]
            return True
        raise serializers.ValidationError(
            {'Period missing': f'Period of fiscal year {activities_obj_date.year} does not exist.'}
        )

    class Meta:
        verbose_name = 'Report Inventory By Month'
        verbose_name_plural = 'Report Inventory By Months'
        ordering = ('-system_date',)
        default_permissions = ()
        permissions = ()


class ReportInventoryProductWarehouse(DataAbstractModel):
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
    sub_period = models.ForeignKey(
        'saledata.SubPeriods',
        on_delete=models.CASCADE,
        related_name='report_inventory_product_warehouse_sub_period',
        null=True,
    )

    opening_balance_quantity = models.FloatField(default=0)
    opening_balance_cost = models.FloatField(default=0)
    opening_balance_value = models.FloatField(default=0)

    ending_balance_quantity = models.FloatField(default=0)
    ending_balance_cost = models.FloatField(default=0)
    ending_balance_value = models.FloatField(default=0)

    for_balance = models.BooleanField(default=False)
    wrong_cost = models.BooleanField(default=False)

    is_close = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Report Inventory Product Warehouse'
        verbose_name_plural = 'Report Inventories Product Warehouse'
        ordering = ()
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_last_sub_period(cls, rp_prd_wh, warehouse_id, period_mapped_id, sub_period_order):
        if sub_period_order > 1:
            for last_item in rp_prd_wh:
                if all([
                    last_item.warehouse_id == warehouse_id,
                    last_item.period_mapped_id == period_mapped_id,
                    last_item.sub_period_order == sub_period_order - 1
                ]):
                    return last_item
            return None
        for last_item in rp_prd_wh:
            period_obj = Periods.objects.filter(id=period_mapped_id).first()
            if period_obj and all([
                last_item.warehouse_id == warehouse_id,
                last_item.period_mapped.fiscal_year == period_obj.fiscal_year - 1,
                last_item.sub_period_order == 12
            ]):
                return last_item
        return None

    def get_value_this_sub_period(
            self,
            data_stock_activity,
            rp_prd_wh,
            warehouse_id,
            period_mapped_id,
            sub_period_order
    ):
        """
        Opening tháng:
            Mặc định là opening của tháng (có thể là số dư đầu kỳ được khai báo | 0)
            Nếu có sub tháng trước (đã khoá sổ): thì lấy ending của tháng trước
        Ending của tháng:
            Mặc định là opening của tháng (có thể là số dư đầu kỳ được khai báo | 0)
            Nếu có giao dịch trong tháng: thì lấy ending của giao dịch cuối cùng
        """
        # Begin get Opening
        last_sub_period = self.get_last_sub_period(
            rp_prd_wh,
            warehouse_id,
            period_mapped_id,
            sub_period_order
        )
        opening_quantity = self.opening_balance_quantity
        opening_value = self.opening_balance_value
        opening_cost = self.opening_balance_cost
        flag = True
        if last_sub_period:
            flag = last_sub_period.is_close
            if flag:
                opening_quantity = last_sub_period.ending_balance_quantity
                opening_value = last_sub_period.ending_balance_value
                opening_cost = last_sub_period.ending_balance_cost
        # End

        # Begin get Ending
        data_stock_activity = sorted(data_stock_activity, key=lambda key: key['system_date'])
        ending_quantity = opening_quantity
        ending_value = opening_value
        ending_cost = opening_cost
        if len(data_stock_activity) > 0:
            ending_quantity = data_stock_activity[-1]['current_quantity']
            ending_value = data_stock_activity[-1]['current_value']
            ending_cost = data_stock_activity[-1]['current_cost']
        # End

        return {
            'is_close': flag,
            'opening_balance_quantity': opening_quantity,
            'opening_balance_value': opening_value,
            'opening_balance_cost': opening_cost,
            'ending_balance_quantity': ending_quantity,
            'ending_balance_value': ending_value,
            'ending_balance_cost': ending_cost
        }
