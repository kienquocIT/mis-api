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
    log_order = models.IntegerField(default=0)

    quantity = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    value = models.FloatField(default=0)

    current_quantity = models.FloatField(default=0)
    current_cost = models.FloatField(default=0)
    current_value = models.FloatField(default=0)

    lot_data = models.JSONField(default=list)

    @classmethod
    def logging_when_stock_activities_happened(cls, activities_obj, activities_obj_date, activities_data):
        """
        Hàm ghi lại các hoạt động tương tác với kho hàng
        Step 1: Tạo log
        Step 2: Cập nhập giá trị tồn kho cho log
        Step 3: Cập nhập giá trị tồn cuối theo kho và update log gần nhất cho kho
        """
        tenant_obj = activities_obj.tenant
        company_obj = activities_obj.company
        fiscal_year = activities_obj_date.year
        period_mapped = Periods.objects.filter(tenant=tenant_obj, company=company_obj, fiscal_year=fiscal_year).first()
        if period_mapped:
            sub_period_order = activities_obj_date.month - period_mapped.space_month
            new_logs = LoggingSubFunction.create_new_logs(
                activities_obj, activities_data, period_mapped, sub_period_order
            )
            new_logs_id_list = [obj.pk for obj in new_logs]
            for log in new_logs:
                log_updated = LoggingSubFunction.update_inventory_value_for_log(
                    log, new_logs_id_list, period_mapped, sub_period_order
                )
                # loại bỏ id của những log đã update rồi
                new_logs_id_list = [log_id for log_id in new_logs_id_list if log_id != log_updated.id]
            return True
        raise serializers.ValidationError({'Period missing': f'Period of fiscal year {fiscal_year} does not exist.'})

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

    class Meta:
        verbose_name = 'Report Inventory Product Warehouse'
        verbose_name_plural = 'Report Inventories Product Warehouse'
        ordering = ()
        default_permissions = ()
        permissions = ()

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
        opening_cost = self.opening_balance_cost
        opening_value = self.opening_balance_value
        # End

        # Begin get Ending
        if len(data_stock_activity) > 0:
            ending_quantity = data_stock_activity[-1]['current_quantity']
            ending_cost = data_stock_activity[-1]['current_cost']
            ending_value = data_stock_activity[-1]['current_value']
        else:
            ending_quantity = opening_quantity
            ending_cost = opening_cost
            ending_value = opening_value
        # End

        return {
            'opening_balance_quantity': opening_quantity,
            'opening_balance_cost': opening_cost,
            'opening_balance_value': opening_value,
            'ending_balance_quantity': ending_quantity,
            'ending_balance_cost': ending_cost,
            'ending_balance_value': ending_value,
        }


class LatestLogByProductWarehouse(SimpleAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='latest_log_product',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='latest_log_warehouse',
    )
    latest_log = models.ForeignKey(
        ReportInventorySub,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = 'Latest Log By Product Warehouse'
        verbose_name_plural = 'Latest Logs By Product Warehouse'
        ordering = ()
        default_permissions = ()
        permissions = ()


class LoggingSubFunction:
    @classmethod
    def create_new_logs(cls, activities_obj, activities_data, period_mapped, sub_period_order):
        """ Step 1: Hàm tạo các log mới """
        bulk_info = []
        log_order_number = 0
        for item in activities_data:
            rp_inventory_obj = ReportInventory.get_report_inventory(
                activities_obj, item['product'], period_mapped, sub_period_order
            )
            # tạo record sub tương ứng để ghi dữ liệu log của các phiếu
            new_log = ReportInventorySub(
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
                lot_data=item.get('lot_data', []),
                log_order=log_order_number
            )
            bulk_info.append(new_log)
            log_order_number += 1
        new_logs = ReportInventorySub.objects.bulk_create(bulk_info)
        return new_logs

    @classmethod
    def update_inventory_value_for_log(cls, log, new_logs_id_list, period_mapped, sub_period_order):
        """ Step 2: Hàm để cập nhập giá trị tồn kho khi log được ghi vào """
        if log.company.companyconfig.definition_inventory_valuation == 0:
            latest_value_list = cls.get_latest_trans_value_list_in_perpetual_inventory(
                log, new_logs_id_list, period_mapped, sub_period_order
            )
            new_value_list = cls.calculate_value_list_in_perpetual_inventory(log, latest_value_list)
            # cập nhập giá trị tồn kho hiện tại mới cho log
            log.current_quantity = new_value_list['quantity']
            log.current_cost = new_value_list['cost']
            log.current_value = new_value_list['value']
            log.save(update_fields=['current_quantity', 'current_cost', 'current_value'])
            cls.update_inventory_cost_data_by_warehouse_this_sub(log, period_mapped, sub_period_order, latest_value_list)
            return log
        if log.company.companyconfig.definition_inventory_valuation == 1:
            latest_value_list = cls.get_latest_trans_value_list_in_periodic_inventory(
                log, new_logs_id_list, period_mapped, sub_period_order
            )
            new_value_list = cls.calculate_value_list_in_periodic_inventory(log, latest_value_list)
            # cập nhập giá trị tồn kho hiện tại mới cho log
            log.current_quantity = new_value_list['quantity']
            log.current_cost = new_value_list['cost']
            log.current_value = new_value_list['value']
            log.save(update_fields=['current_quantity', 'current_cost', 'current_value'])
            cls.update_inventory_cost_data_by_warehouse_this_sub(log, period_mapped, sub_period_order, latest_value_list)
            return log
        raise serializers.ValidationError({'Company config': 'Company inventory valuation config must be 0 or 1.'})

    @classmethod
    def update_inventory_cost_data_by_warehouse_this_sub(cls, log, period_mapped, sub_period_order, latest_value_list):
        """
        Step 3: Hàm kiểm tra record quản lí giá cost của sp theo từng kho trong kì nay đã có hay chưa ?
        Chưa thì tạo mới - Có thì Update lại quantity-cost-value
        """
        sub_period_obj = period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            inventory_cost_data_item = ReportInventoryProductWarehouse.objects.filter(
                tenant_id=period_mapped.tenant_id,
                company_id=period_mapped.company_id,
                product=log.product,
                warehouse=log.warehouse,
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj
            ).first()
            if not inventory_cost_data_item:
                inventory_cost_data_item = ReportInventoryProductWarehouse.objects.create(
                    tenant_id=period_mapped.tenant_id,
                    company_id=period_mapped.company_id,
                    product=log.product,
                    warehouse=log.warehouse,
                    period_mapped=period_mapped,
                    sub_period_order=sub_period_order,
                    sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                    opening_balance_quantity=latest_value_list['quantity'],
                    opening_balance_cost=latest_value_list['cost'],
                    opening_balance_value=latest_value_list['value'],
                    ending_balance_quantity=log.current_quantity,
                    ending_balance_cost=log.current_cost,
                    ending_balance_value=log.current_value,
                )
            else:
                inventory_cost_data_item.ending_balance_quantity = log.current_quantity
                inventory_cost_data_item.ending_balance_cost = log.current_cost
                inventory_cost_data_item.ending_balance_value = log.current_value
                inventory_cost_data_item.save(update_fields=[
                    'ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value'
                ])

            latest_log_obj = log.product.latest_log_product.filter(warehouse=log.warehouse).first()
            if latest_log_obj:
                latest_log_obj.latest_log = log
                latest_log_obj.save(update_fields=['latest_log'])
            else:
                LatestLogByProductWarehouse.objects.create(
                    product=log.product, warehouse=log.warehouse, latest_log=log
                )

            return inventory_cost_data_item
        raise serializers.ValidationError({'Sub period missing': 'Sub period of this period does not exist.'})

    @classmethod
    def get_latest_trans(cls, prd_id, wh_id, period_mapped, sub_period_order, by_month=False, **kwargs):
        """
        Hàm để lấy giao dịch gần nhất (mặc định lấy gần nhất).
        Nếu tham số by_month == True: lấy giao dịch end month của tháng gần nhất.
        *** Parameter 'exclude_list_by_id' (list id các obj ReportInventorySub), để bỏ các obj sinh ra khi chưa save
        """
        if by_month:
            # để tránh TH lấy hết records lên thì sẽ lấy ưu tiên theo thứ tự:
            # 1: lấy records các tháng trước (trong năm)
            # 2: lấy records các năm trước
            end_month_subs = ReportInventorySub.objects.filter(
                product_id=prd_id, warehouse_id=wh_id,
                report_inventory__period_mapped=period_mapped,
                report_inventory__sub_period_order__lt=sub_period_order
            )
            if end_month_subs.count() == 0:
                end_month_subs = ReportInventorySub.objects.filter(
                    product_id=prd_id, warehouse_id=wh_id,
                    report_inventory__period_mapped__fiscal_year__lt=period_mapped.fiscal_year
                )
            latest_trans = end_month_subs.latest('date_created') if end_month_subs.count() > 0 else None
        else:
            # để tránh TH lấy hết records lên thì sẽ lấy ưu tiên theo thứ tự:
            # 1: lấy records tháng này
            # 2: lấy records các tháng trước (trong năm)
            # 3: lấy records các năm trước
            # exclude_list_by_id = kwargs['exclude_list_by_id'] if 'exclude_list_by_id' in kwargs else []
            # subs = ReportInventorySub.objects.filter(
            #     product_id=prd_id, warehouse_id=wh_id,
            #     report_inventory__period_mapped=period_mapped,
            #     report_inventory__sub_period_order=sub_period_order
            # ).exclude(id__in=exclude_list_by_id)
            # if subs.count() == 0:
            #     subs = ReportInventorySub.objects.filter(
            #         product_id=prd_id, warehouse_id=wh_id,
            #         report_inventory__period_mapped=period_mapped,
            #         report_inventory__sub_period_order__lt=sub_period_order
            #     ).exclude(id__in=exclude_list_by_id)
            #     if subs.count() == 0:
            #         subs = ReportInventorySub.objects.filter(
            #             product_id=prd_id, warehouse_id=wh_id,
            #             report_inventory__period_mapped__fiscal_year__lt=period_mapped.fiscal_year
            #         ).exclude(id__in=exclude_list_by_id)
            # latest_trans = subs.latest('date_created') if subs.count() > 0 else None

            subs = LatestLogByProductWarehouse.objects.filter(
                product_id=prd_id, warehouse_id=wh_id
            ).order_by(
                '-latest_log__report_inventory__period_mapped__fiscal_year',
                '-latest_log__report_inventory__sub_period_order',
            )
            latest_trans = subs.first() if subs.count() > 0 else None

        return latest_trans

    @classmethod
    def get_latest_trans_value_list_in_perpetual_inventory(cls, log, new_logs_id_list, period_mapped, sub_period_order):
        """ Hàm tìm giao dịch gần nhất (theo sp và kho) """
        if log.company.companyconfig.definition_inventory_valuation == 0:
            latest_trans = LoggingSubFunction.get_latest_trans(
                log.product_id, log.warehouse_id, period_mapped, sub_period_order, False,
                **{'exclude_list_by_id': new_logs_id_list}
            )
            if latest_trans:
                value_list = {
                    'quantity': latest_trans.current_quantity,
                    'cost': latest_trans.current_cost,
                    'value': latest_trans.current_value
                }
                return value_list
            return {'quantity': log.quantity, 'cost': log.cost, 'value': log.value}
        if log.company.companyconfig.definition_inventory_valuation == 1:
            sub_list = ReportInventorySub.objects.filter(
                product=log.product,
                warehouse=log.warehouse
            ).exclude(id__in=new_logs_id_list)
            latest_trans = sub_list.latest('date_created') if sub_list.count() > 0 else None
            if latest_trans:
                value_list = {
                    'quantity': latest_trans.current_quantity,
                    'cost': latest_trans.current_cost,
                    'value': latest_trans.current_value
                }
                return value_list
            return {'quantity': log.quantity, 'cost': log.cost, 'value': log.value}
        raise serializers.ValidationError({'Company config': 'Company inventory valuation config must be 0 or 1.'})

    @classmethod
    def get_latest_trans_value_list_in_periodic_inventory(cls, log, new_logs_id_list, period_mapped, sub_period_order):
        """ Hàm tìm giao dịch gần nhất (theo sp và kho) """
        if log.company.companyconfig.definition_inventory_valuation == 0:
            latest_trans = LoggingSubFunction.get_latest_trans(
                log.product_id, log.warehouse_id, period_mapped, sub_period_order, False,
                **{'exclude_list_by_id': new_logs_id_list}
            )
            if latest_trans:
                value_list = {
                    'quantity': latest_trans.current_quantity,
                    'cost': latest_trans.current_cost,
                    'value': latest_trans.current_value
                }
                return value_list
            return {'quantity': log.quantity, 'cost': log.cost, 'value': log.value}
        if log.company.companyconfig.definition_inventory_valuation == 1:
            sub_list = ReportInventorySub.objects.filter(
                product=log.product,
                warehouse=log.warehouse
            ).exclude(id__in=new_logs_id_list)
            latest_trans = sub_list.latest('date_created') if sub_list.count() > 0 else None
            if latest_trans:
                value_list = {
                    'quantity': latest_trans.current_quantity,
                    'cost': latest_trans.current_cost,
                    'value': latest_trans.current_value
                }
                return value_list
            return {'quantity': log.quantity, 'cost': log.cost, 'value': log.value}
        raise serializers.ValidationError({'Company config': 'Company inventory valuation config must be 0 or 1.'})

    @classmethod
    def calculate_value_list_in_perpetual_inventory(cls, log, latest_value_list):
        """ Hàm tính toán cho Phương pháp Kê khai thường xuyên """
        if log.stock_type == 1:
            new_quantity = latest_value_list['quantity'] + log.quantity
            sum_value = latest_value_list['value'] + log.value
            new_cost = sum_value / new_quantity
            new_value = sum_value
        else:
            new_quantity = latest_value_list['quantity'] - log.quantity
            new_cost = latest_value_list['cost']
            new_value = new_cost * new_quantity
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def calculate_value_list_in_periodic_inventory(cls, log, latest_value_list):
        """ Hàm tính toán cho Phương pháp Kiểm kê định kì """
        if log.stock_type == 1:
            new_quantity = latest_value_list['quantity'] + log.quantity
            sum_value = latest_value_list['value'] + log.value
            new_cost = sum_value / new_quantity
            new_value = sum_value
        else:
            new_quantity = latest_value_list['quantity'] - log.quantity
            new_cost = latest_value_list['cost']
            new_value = new_cost * new_quantity
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}
