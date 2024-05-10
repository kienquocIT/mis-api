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
    def get_report_inventory(cls, activities_obj, product_obj, period_mapped, sub_period_order):
        sub_period_obj = period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        tenant_obj = activities_obj.tenant
        company_obj = activities_obj.company
        emp_inherit_obj = activities_obj.employee_inherit
        emp_created_obj = activities_obj.employee_created if activities_obj.employee_created else emp_inherit_obj
        if sub_period_obj:
            # (obj này là root) - có thì return, chưa có thì tạo mới
            report_inventory_obj = cls.objects.filter(
                tenant=tenant_obj,
                company=company_obj,
                product=product_obj,
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj
            ).first()
            if not report_inventory_obj:
                report_inventory_obj = cls.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    employee_created=emp_created_obj,
                    employee_inherit=emp_inherit_obj,
                    product=product_obj,
                    period_mapped=period_mapped,
                    sub_period_order=sub_period_order,
                    sub_period=sub_period_obj
                )
            return report_inventory_obj
        raise serializers.ValidationError({'Sub period missing': 'Sub period object does not exist.'})

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
    def create_new_log(cls, activities_obj, activities_data, period_mapped, activities_obj_date):
        sub_period_order = activities_obj_date - period_mapped.space_month
        bulk_info = []
        for item in activities_data:
            rp_inventory_obj = ReportInventory.get_report_inventory(
                activities_obj, item['product'], period_mapped, sub_period_order
            )
            # tạo record sub tương ứng để ghi dữ liệu log của các phiếu
            new_log = cls(
                tenant=activities_obj.tenant,
                company=activities_obj.company,
                report_inventory=rp_inventory_obj,
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
    def get_latest_trans(cls, log, new_logs_id_list):
        """ Hàm tìm giao dịch gần nhất (theo sp và kho) """
        sub_list = ReportInventorySub.objects.filter(
            product=log.product,
            warehouse=log.warehouse
        ).exclude(id__in=new_logs_id_list)
        latest_trans = sub_list.latest('date_created') if sub_list.count() > 0 else None
        return latest_trans

    @classmethod
    def check_inventory_cost_data_by_warehouse_this_sub(cls, log, period_mapped, sub_period_order, value_list):
        """ Hàm kiểm tra record quản lí giá cost của sp theo từng kho trong kì nay đã có hay chưa ? Chưa thì tạo mới"""
        inventory_cost_data_item = ReportInventoryProductWarehouse.objects.filter(
            tenant_id=period_mapped.tenant_id,
            company_id=period_mapped.company_id,
            product=log.product,
            warehouse=log.warehouse,
            period_mapped=period_mapped,
            sub_period_order=sub_period_order,
            sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        ).exists()
        if not inventory_cost_data_item:
            ReportInventoryProductWarehouse.objects.create(
                tenant_id=period_mapped.tenant_id,
                company_id=period_mapped.company_id,
                product=log.product,
                warehouse=log.warehouse,
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                opening_balance_quantity=value_list['quantity'],
                opening_balance_cost=value_list['cost'],
                opening_balance_value=value_list['value']
            )
        return True

    @classmethod
    def process_log_current_data(cls, log, value_list):
        if log.stock_type == 1:
            new_quantity = value_list['quantity'] + log.quantity
            sum_value = value_list['value'] + log.value
            new_cost = sum_value / new_quantity
            new_value = sum_value
        else:
            new_quantity = value_list['quantity'] - log.quantity
            new_cost = value_list['cost']
            new_value = new_cost * new_quantity
        return {'new_quantity': new_quantity, 'new_cost': new_cost, 'new_value': new_value}

    @classmethod
    def update_inventory_value_for_log(cls, log, new_logs_id_list, period_mapped, sub_period_order):
        """ Hàm để cập nhập giá trị tồn kho cho từng log """
        # tìm giao dịch gần nhất để lấy các giá trị (SL, cost, value)
        latest_trans = cls.get_latest_trans(log, new_logs_id_list)
        [new_opening_quantity, new_opening_cost, new_opening_value] = [
            latest_trans.current_quantity, latest_trans.current_cost, latest_trans.current_value
        ] if latest_trans else [0, 0, 0]
        # check xem record quản lí giá cost theo kho trong kì này đã có chưa? chưa thì tạo mới
        cls.check_inventory_cost_data_by_warehouse_this_sub(
            log, period_mapped, sub_period_order,
            {
                'quantity': new_opening_quantity,
                'cost': new_opening_cost,
                'value': new_opening_value
            }
        )
        # xử lí giá trị tồn kho hiện tại cho từng lần nhập-xuất
        value_list = cls.process_log_current_data(
            log,
            {
                'quantity': new_opening_quantity,
                'cost': new_opening_cost,
                'value': new_opening_value
            }
        )
        # cập nhập giá trị tồn kho hiện tại cho log
        log.current_quantity = value_list['new_quantity']
        log.current_cost = value_list['new_cost']
        log.current_value = value_list['new_value']
        log.save(update_fields=['current_quantity', 'current_cost', 'current_value'])
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
            # tạo các log mới
            new_logs, new_logs_id_list = cls.create_new_log(
                activities_obj, activities_data, period_mapped, activities_obj_date.month
            )
            # cho từng log, cập nhập giá trị tồn kho
            for log in new_logs:
                log_return = cls.update_inventory_value_for_log(log, new_logs_id_list, period_mapped, sub_period_order)
                # id của những log đã tạo
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

    class Meta:
        verbose_name = 'Report Inventory Product Warehouse'
        verbose_name_plural = 'Report Inventories Product Warehouse'
        ordering = ()
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_inventory_cost_data_last_sub_period(
            cls,
            inventory_cost_data_list,
            warehouse_id,
            period_mapped_id,
            sub_period_order
    ):
        if sub_period_order > 1:
            for inventory_cost_data in inventory_cost_data_list:
                if all([
                    inventory_cost_data.warehouse_id == warehouse_id,
                    inventory_cost_data.period_mapped_id == period_mapped_id,
                    inventory_cost_data.sub_period_order == sub_period_order - 1
                ]):
                    return inventory_cost_data
            return None
        for inventory_cost_data in inventory_cost_data_list:
            period_obj = Periods.objects.filter(id=period_mapped_id).first()
            if period_obj and all([
                inventory_cost_data.warehouse_id == warehouse_id,
                inventory_cost_data.period_mapped.fiscal_year == period_obj.fiscal_year - 1,
                inventory_cost_data.sub_period_order == 12
            ]):
                return inventory_cost_data
        return None

    def get_inventory_cost_data_this_sub_period(self, data_stock_activity):
        """
        Opening tháng:
            Mặc định là opening của tháng
        Ending của tháng:
            Mặc định là opening của tháng
            Nếu có giao dịch trong tháng: thì lấy ending của giao dịch cuối cùng
        """
        # Begin get Opening
        opening_quantity = self.opening_balance_quantity
        opening_value = self.opening_balance_value
        opening_cost = self.opening_balance_cost
        # End

        # Begin get Ending
        ending_quantity = opening_quantity
        ending_value = opening_value
        ending_cost = opening_cost
        if len(data_stock_activity) > 0:
            ending_quantity = data_stock_activity[-1]['current_quantity']
            ending_value = data_stock_activity[-1]['current_value']
            ending_cost = data_stock_activity[-1]['current_cost']
        # End

        return {
            'opening_balance_quantity': opening_quantity,
            'opening_balance_value': opening_value,
            'opening_balance_cost': opening_cost,
            'ending_balance_quantity': ending_quantity,
            'ending_balance_value': ending_value,
            'ending_balance_cost': ending_cost
        }
