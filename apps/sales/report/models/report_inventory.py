from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods, Product, WareHouse, SubPeriods
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

    quantity = models.FloatField(default=0, help_text='is sum input quantity in perpetual')
    cost = models.FloatField(default=0, help_text='is sum input quantity in perpetual')
    value = models.FloatField(default=0, help_text='is sum input quantity in perpetual')

    current_quantity = models.FloatField(default=0, help_text='is quantity current in perpetual')
    current_cost = models.FloatField(default=0, help_text='is cost current in perpetual')
    current_value = models.FloatField(default=0, help_text='is value current in perpetual')

    periodic_current_quantity = models.FloatField(default=0, help_text='is quantity current in periodic')
    periodic_current_cost = models.FloatField(default=0, help_text='is cost current in periodic')
    periodic_current_value = models.FloatField(default=0, help_text='is value current in periodic')

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

            if company_obj.companyconfig.definition_inventory_valuation == 1:
                if sub_period_order == 1:
                    last_period = Periods.objects.filter(
                        tenant=tenant_obj, company=company_obj,
                        fiscal_year=period_mapped.fiscal_year - 1
                    ).first()
                    last_sub_record = ReportInventoryProductWarehouse.objects.filter(
                        period_mapped=last_period,
                        sub_period_order=12,
                        periodic_closed=False
                    ).exists()
                    if last_sub_record:
                        LoggingSubFunction.calculate_ending_cumulative_value(
                            last_period, 12, tenant_obj, company_obj
                        )
                else:
                    last_sub_record = ReportInventoryProductWarehouse.objects.filter(
                        period_mapped=period_mapped,
                        sub_period_order=sub_period_order - 1,
                        periodic_closed=False
                    ).exists()
                    if last_sub_record:
                        LoggingSubFunction.calculate_ending_cumulative_value(
                            period_mapped, sub_period_order - 1, tenant_obj, company_obj
                        )

            new_logs = cls.create_new_logs(activities_obj, activities_data, period_mapped, sub_period_order)
            for log in new_logs:
                cls.update_inventory_value_for_log(log, period_mapped, sub_period_order)
            return True
        raise serializers.ValidationError({'Period missing': f'Period of fiscal year {fiscal_year} does not exist.'})

    @classmethod
    def create_new_logs(cls, activities_obj, activities_data, period_mapped, sub_period_order):
        """ Step 1: Hàm tạo các log mới """
        bulk_info = []
        log_order_number = 0
        for item in activities_data:
            report_inventory_obj = ReportInventory.get_report_inventory(
                activities_obj, item['product'], period_mapped, sub_period_order
            )

            div = activities_obj.company.companyconfig.definition_inventory_valuation
            cost = LoggingSubFunction.get_latest_value(
                item['product'].id, item['warehouse'].id, period_mapped, div
            )['cost'] if item['stock_type'] == -1 else item['cost']

            # tạo log
            new_log = cls(
                tenant=activities_obj.tenant,
                company=activities_obj.company,
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
                cost=cost,
                value=cost * item['quantity'],
                lot_data=item.get('lot_data', []),
                log_order=log_order_number
            )
            bulk_info.append(new_log)
            log_order_number += 1
        new_logs = cls.objects.bulk_create(bulk_info)
        return new_logs

    @classmethod
    def update_inventory_value_for_log(cls, log, period_mapped, sub_period_order):
        """ Step 2: Hàm để cập nhập giá trị tồn kho khi log được ghi vào """
        div = log.company.companyconfig.definition_inventory_valuation
        if div == 0:
            # lấy value list của log gần nhất (nếu k, lấy số dư đầu kì)
            latest_value = LoggingSubFunction.get_latest_value(log.product_id, log.warehouse_id, period_mapped, div)
            # tính toán value list mới
            new_value_list = LoggingSubFunction.calculate_new_value_list_in_perpetual_inventory(log, latest_value)
            # cập nhập giá trị tồn kho hiện tại mới cho log
            log.current_quantity = new_value_list['quantity']
            log.current_cost = new_value_list['cost']
            log.current_value = new_value_list['value']
            log.save(update_fields=['current_quantity', 'current_cost', 'current_value'])
            cls.update_inventory_cost_data_by_warehouse_this_sub(
                log, period_mapped, sub_period_order, latest_value, div
            )
            return True
        if div == 1:
            # lấy value list của log gần nhất (nếu k, lấy số dư đầu kì)
            latest_value = LoggingSubFunction.get_latest_value(log.product_id, log.warehouse_id, period_mapped, div)
            # tính toán value list mới
            new_value_list = LoggingSubFunction.calculate_new_value_list_in_periodic_inventory(log, latest_value)
            # cập nhập giá trị tồn kho hiện tại mới cho log
            log.periodic_current_quantity = new_value_list['quantity']
            log.periodic_current_cost = new_value_list['cost']  # = 0
            log.periodic_current_value = new_value_list['value']  # = 0
            log.save(update_fields=['periodic_current_quantity', 'periodic_current_cost', 'periodic_current_value'])
            cls.update_inventory_cost_data_by_warehouse_this_sub(
                log, period_mapped, sub_period_order, latest_value, div
            )
            return True
        raise serializers.ValidationError({'Company config': 'Company inventory valuation config must be 0 or 1.'})

    @classmethod
    def update_inventory_cost_data_by_warehouse_this_sub(cls, log, period_mapped, sub_period_order, latest_value, div):
        """
        Step 3: Hàm kiểm tra record quản lí giá cost của sp theo từng kho trong kì nay đã có hay chưa ?
        Chưa thì tạo mới - Có thì Update lại quantity-cost-value
        """
        sub_period_obj = period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            # tìm record
            inventory_cost_data_item = ReportInventoryProductWarehouse.objects.filter(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                product=log.product,
                warehouse=log.warehouse,
                period_mapped=period_mapped,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj
            ).first()

            # nếu kiểm kê thường xuyên
            if div == 0:
                if not inventory_cost_data_item:  # không có thì tạo, gán log
                    inventory_cost_data_item = ReportInventoryProductWarehouse.objects.create(
                        tenant_id=log.tenant_id,
                        company_id=log.company_id,
                        product=log.product,
                        warehouse=log.warehouse,
                        period_mapped=period_mapped,
                        sub_period_order=sub_period_order,
                        sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                        opening_balance_quantity=latest_value['quantity'],
                        opening_balance_cost=latest_value['cost'],
                        opening_balance_value=latest_value['value'],
                        ending_balance_quantity=log.current_quantity,
                        ending_balance_cost=log.current_cost,
                        ending_balance_value=log.current_value,
                        sub_latest_log=log
                    )
                else:  # nếu có thì update giá cost, gán sub
                    inventory_cost_data_item.ending_balance_quantity = log.current_quantity
                    inventory_cost_data_item.ending_balance_cost = log.current_cost
                    inventory_cost_data_item.ending_balance_value = log.current_value
                    inventory_cost_data_item.sub_latest_log = log
                    inventory_cost_data_item.save(update_fields=[
                        'ending_balance_quantity', 'ending_balance_cost', 'ending_balance_value', 'sub_latest_log'
                    ])
            else:
                # nếu kiểm kê định kì
                if not inventory_cost_data_item:  # nếu không có thì tạo, gán log
                    inventory_cost_data_item = ReportInventoryProductWarehouse.objects.create(
                        tenant_id=log.tenant_id,
                        company_id=log.company_id,
                        product=log.product,
                        warehouse=log.warehouse,
                        period_mapped=period_mapped,
                        sub_period_order=sub_period_order,
                        sub_period=period_mapped.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                        opening_balance_quantity=latest_value['quantity'],
                        opening_balance_cost=latest_value['cost'],
                        opening_balance_value=latest_value['value'],
                        periodic_ending_balance_quantity=log.current_quantity,
                        periodic_ending_balance_cost=log.current_cost,
                        periodic_ending_balance_value=log.current_value,
                        sub_latest_log=log
                    )
                else:  # có thì cập nhập
                    if log.stock_type == 1:
                        # nếu là input thì cộng tổng SL nhập và tổng Value nhập
                        inventory_cost_data_item.sum_input_quantity += log.quantity
                        inventory_cost_data_item.sum_input_value += log.quantity * log.cost
                    else:
                        # nếu là xuất thì cập nhập SL xuất
                        inventory_cost_data_item.sum_output_quantity += log.quantity

                    # update giá cost
                    inventory_cost_data_item.periodic_ending_balance_quantity = log.periodic_current_quantity
                    inventory_cost_data_item.periodic_ending_balance_cost = log.periodic_current_cost
                    inventory_cost_data_item.periodic_ending_balance_value = log.periodic_current_value
                    # nếu kì đã đóng mà có giao dịch, mở lại, cost-value hiện tại trở về 0 (chưa chốt)
                    if inventory_cost_data_item.periodic_closed:
                        inventory_cost_data_item.periodic_closed = False
                        inventory_cost_data_item.periodic_ending_balance_cost = 0
                        inventory_cost_data_item.periodic_ending_balance_value = 0
                    inventory_cost_data_item.save(update_fields=[
                        'periodic_ending_balance_quantity',
                        'periodic_ending_balance_cost',
                        'periodic_ending_balance_value',
                        'sum_output_quantity',
                        'sum_input_quantity',
                        'sum_input_value',
                        'periodic_closed'
                    ])

            # cập nhập log mới nhất, không có thì tạo mới
            latest_log_obj = log.product.latest_log_product.filter(warehouse=log.warehouse).first()
            if latest_log_obj:
                latest_log_obj.latest_log = log
                latest_log_obj.save(update_fields=['latest_log'])
            else:
                LatestSub.objects.create(
                    product=log.product, warehouse=log.warehouse, latest_log=log
                )

            return inventory_cost_data_item
        raise serializers.ValidationError({'Sub period missing': 'Sub period of this period does not exist.'})

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

    ending_balance_quantity = models.FloatField(default=0, help_text='is ending balance quantity in perpetual')
    ending_balance_cost = models.FloatField(default=0, help_text='is ending balance cost in perpetual')
    ending_balance_value = models.FloatField(default=0, help_text='is ending balance value in perpetual')

    periodic_ending_balance_quantity = models.FloatField(default=0, help_text='is ending balance quantity in periodic')
    periodic_ending_balance_cost = models.FloatField(default=0, help_text='is ending balance cost in periodic')
    periodic_ending_balance_value = models.FloatField(default=0, help_text='is ending balance value in periodic')

    sum_input_quantity = models.FloatField(default=0, help_text='is sum input quantity in periodic')
    sum_input_value = models.FloatField(default=0, help_text='is sum value quantity in periodic')
    sum_output_quantity = models.FloatField(default=0, help_text='is sum output quantity in periodic')
    periodic_closed = models.BooleanField(default=False, help_text='is True if sub has closed')

    for_balance = models.BooleanField(default=False, help_text='is True if it has balance')
    sub_latest_log = models.ForeignKey(
        ReportInventorySub,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = 'Report Inventory Product Warehouse'
        verbose_name_plural = 'Report Inventories Product Warehouse'
        ordering = ()
        default_permissions = ()
        permissions = ()


class LatestSub(SimpleAbstractModel):
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
    def get_latest_trans(cls, prd_id, wh_id):
        latest_logs = LatestSub.objects.filter(product_id=prd_id, warehouse_id=wh_id).first()
        latest_trans = latest_logs.latest_log if latest_logs else None
        return latest_trans

    @classmethod
    def get_latest_trans_by_month(cls, prd_id, wh_id, period_mapped, sub_period_order):
        """
        Hàm để lấy giao dịch cuối cùng của tháng trước.
        """
        # ưu tiên theo thứ tự:
        # 1: lấy records các tháng trước (trong năm)
        # 2: Nếu 1 không có, lấy records các năm trước
        end_month_subs = ReportInventoryProductWarehouse.objects.filter(
            product_id=prd_id, warehouse_id=wh_id, period_mapped=period_mapped, sub_period_order__lt=sub_period_order
        ).first()
        latest_trans = end_month_subs.sub_latest_log if end_month_subs else None
        if end_month_subs:
            end_month_subs = LatestSub.objects.filter(product_id=prd_id, warehouse_id=wh_id).first()
            latest_trans = end_month_subs.latest_log if end_month_subs else None
        return latest_trans

    @classmethod
    def get_latest_value(cls, product_id, warehouse_id, period_mapped, div):
        """ Hàm tìm giao dịch gần nhất (theo sp và kho) """
        latest_trans = LoggingSubFunction.get_latest_trans(product_id, warehouse_id)
        if latest_trans:
            value_list = {
                'quantity': latest_trans.current_quantity,
                'cost': latest_trans.current_cost,
                'value': latest_trans.current_value
            } if div == 0 else {
                'quantity': latest_trans.periodic_current_quantity,
                'cost': latest_trans.periodic_current_cost,
                'value': latest_trans.periodic_current_value
            }
            return value_list
        return cls.get_opening_balance_data(product_id, warehouse_id, period_mapped, 3)

    @classmethod
    def calculate_new_value_list_in_perpetual_inventory(cls, log, latest_value):
        """ Hàm tính toán cho Phương pháp Kê khai thường xuyên """
        if log.stock_type == 1:
            new_quantity = latest_value['quantity'] + log.quantity
            sum_value = latest_value['value'] + log.value
            new_cost = sum_value / new_quantity
            new_value = sum_value
        else:
            new_quantity = latest_value['quantity'] - log.quantity
            new_cost = latest_value['cost']
            new_value = new_cost * new_quantity
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def calculate_new_value_list_in_periodic_inventory(cls, log, latest_value):
        """ Hàm tính toán cho Phương pháp Kiểm kê định kì """
        if log.stock_type == 1:
            # Lúc này sum nhập đã được cập nhập
            new_quantity = latest_value['quantity'] + log.quantity
            new_cost = 0
            new_value = 0
        else:
            new_quantity = latest_value['quantity'] - log.quantity
            new_cost = 0
            new_value = 0
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def get_opening_balance_data(cls, product_id, warehouse_id, period_mapped, data_type=1):
        """
        Hàm để lấy Số dư đầu kì theo SP và KHO
        (0-quantity, 1-cost, 2-value, 3-{'quantity':, 'cost':, 'value':}, else-return1)
        """
        # tìm số dư đầu kì
        opening_value_list_obj = ReportInventoryProductWarehouse.objects.filter(
            product_id=product_id, warehouse_id=warehouse_id, period_mapped=period_mapped, for_balance=True
        ).first()
        if opening_value_list_obj:
            if data_type == 0:
                return opening_value_list_obj.opening_balance_quantity
            if data_type == 1:
                return opening_value_list_obj.opening_balance_cost
            if data_type == 2:
                return opening_value_list_obj.opening_balance_value
            if data_type == 3:
                return {
                    'quantity': opening_value_list_obj.opening_balance_quantity,
                    'cost': opening_value_list_obj.opening_balance_cost,
                    'value': opening_value_list_obj.opening_balance_value
                }
            return opening_value_list_obj.opening_balance_cost
        return 0 if data_type != 3 else {'quantity': 0, 'cost': 0, 'value': 0}

    @classmethod
    def get_inventory_cost_data_this_sub_period(cls, inventory_cost_data_obj, data_stock_activity):
        """
        Opening tháng:
            Mặc định là opening của tháng
        Ending của tháng:
            Mặc định là opening của tháng
            Nếu có giao dịch trong tháng: thì lấy ending của giao dịch cuối cùng
        """
        # Begin get Opening
        opening_quantity = inventory_cost_data_obj.opening_balance_quantity
        opening_cost = inventory_cost_data_obj.opening_balance_cost
        opening_value = inventory_cost_data_obj.opening_balance_value
        # End

        # Begin get Ending
        if len(data_stock_activity) > 0:
            if inventory_cost_data_obj.company.companyconfig == 0:
                ending_quantity = data_stock_activity[-1]['current_quantity']
                ending_cost = data_stock_activity[-1]['current_cost']
                ending_value = data_stock_activity[-1]['current_value']
            else:
                ending_quantity = inventory_cost_data_obj.periodic_ending_balance_quantity
                ending_cost = inventory_cost_data_obj.periodic_ending_balance_cost
                ending_value = inventory_cost_data_obj.periodic_ending_balance_value
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

    @classmethod
    def calculate_ending_cumulative_value(cls, period_mapped, sub_period_order, tenant, company):
        product_id_list = set(Product.objects.filter(tenant=tenant, company=company).values_list('id', flat=True))
        warehouse_id_list = set(WareHouse.objects.filter(tenant=tenant, company=company).values_list('id', flat=True))
        for warehouse_id in warehouse_id_list:
            for product_id in product_id_list:
                inventory_cost_data_obj = ReportInventoryProductWarehouse.objects.filter(
                    period_mapped=period_mapped, sub_period_order=sub_period_order,
                    product_id=product_id, warehouse_id=warehouse_id
                ).first()
                if inventory_cost_data_obj:
                    if not inventory_cost_data_obj.periodic_closed:
                        sum_input_quantity = inventory_cost_data_obj.sum_input_quantity
                        sum_input_value = inventory_cost_data_obj.sum_input_value
                        sum_output_quantity = inventory_cost_data_obj.sum_output_quantity

                        if sum_input_quantity > 0:
                            value_list = {
                                'quantity': sum_input_quantity - sum_output_quantity,
                                'cost': sum_input_value / sum_input_quantity,
                                'value': (sum_input_quantity - sum_output_quantity) * (sum_input_value / sum_input_quantity)
                            }
                        else:
                            value_list = {
                                'quantity': inventory_cost_data_obj.opening_balance_quantity,
                                'cost': inventory_cost_data_obj.opening_balance_quantity,
                                'value': inventory_cost_data_obj.opening_balance_quantity
                            }

                        inventory_cost_data_obj.periodic_ending_balance_quantity = value_list['quantity']
                        inventory_cost_data_obj.periodic_ending_balance_cost = value_list['cost']
                        inventory_cost_data_obj.periodic_ending_balance_value = value_list['value']
                        inventory_cost_data_obj.periodic_closed = True
                        inventory_cost_data_obj.save(update_fields=[
                            'periodic_ending_balance_quantity',
                            'periodic_ending_balance_cost',
                            'periodic_ending_balance_value',
                            'periodic_closed'
                        ])
        return True
