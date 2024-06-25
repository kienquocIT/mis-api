from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods
from apps.shared import DataAbstractModel, SimpleAbstractModel


class ReportInventory(DataAbstractModel):  # rp_inventory
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_inventory_product',
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='report_inventory_lot_mapped',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_inventory_sale_order",
        null=True
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
    def get_report_inventory(
            cls, tenant_obj, company_obj, emp_created_obj, emp_inherit_obj, period_obj, sub_period_order,
            product_obj, **kwargs
    ):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        - option 2: [lot_mapped_id]
        - option 3: [warehouse_id, lot_mapped_id]
        - option 4: [sale_order_id]
        """
        if 'warehouse_id' in kwargs:
            del kwargs['warehouse_id']
        sub_period_obj = period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            # (obj này là root) - có thì return, chưa có thì tạo mới
            rp_inventory = cls.objects.filter(
                tenant=tenant_obj,
                company=company_obj,
                product=product_obj,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                **kwargs
            ).first()
            if not rp_inventory:
                rp_inventory = cls.objects.create(
                    tenant=tenant_obj,
                    company=company_obj,
                    employee_created=emp_created_obj if emp_created_obj else emp_inherit_obj,
                    employee_inherit=emp_inherit_obj if emp_inherit_obj else emp_created_obj,
                    product=product_obj,
                    period_mapped=period_obj,
                    sub_period_order=sub_period_order,
                    sub_period=sub_period_obj,
                    **kwargs
                )
            return rp_inventory
        raise serializers.ValidationError({'Sub period missing': 'Sub period object does not exist.'})

    class Meta:
        verbose_name = 'Report Inventory'
        verbose_name_plural = 'Report Inventories'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()


class ReportInventorySub(DataAbstractModel):  # rp_sub
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
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='report_inventory_by_month_lot_mapped',
        null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_inventory_by_month_warehouse',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_inventory_by_month_sale_order",
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
    def get_config_inventory_management(cls, company_config):
        cost_per_warehouse = company_config.cost_per_warehouse
        cost_per_lot = company_config.cost_per_lot
        cost_per_project = company_config.cost_per_project
        config_inventory_management = []
        if cost_per_warehouse:
            config_inventory_management.append(1)
        if cost_per_lot:
            config_inventory_management.append(2)
        if cost_per_project:
            config_inventory_management.append(3)
        return config_inventory_management

    @classmethod
    def cast_quantity_to_unit(cls, log_uom, log_quantity):
        return log_quantity * log_uom.ratio

    @classmethod
    def logging_when_stock_activities_happened(cls, stock_obj, stock_obj_date, stock_data):
        """
        Hàm ghi lại các hoạt động tương tác với kho hàng
        Step 1: Tạo log
        Step 2: Cập nhập giá trị tồn kho cho log
        Step 3: Cập nhập giá trị tồn cuối theo kho và update log gần nhất cho kho
        """
        config_inventory_management = cls.get_config_inventory_management(stock_obj.company.company_config)
        period_obj = Periods.objects.filter(
            tenant=stock_obj.tenant,
            company=stock_obj.company,
            fiscal_year=stock_obj_date.year
        ).first()
        if period_obj:
            sub_period_order = stock_obj_date.month - period_obj.space_month
            if stock_obj.company.company_config.definition_inventory_valuation == 1:
                if int(sub_period_order) == 1:
                    last_period = Periods.objects.filter(
                        tenant=stock_obj.tenant,
                        company=stock_obj.company,
                        fiscal_year=period_obj.fiscal_year - 1
                    ).first()
                    last_sub_record = ReportInventoryProductWarehouse.objects.filter(
                        period_mapped=last_period,
                        sub_period_order=12,
                        periodic_closed=False
                    ).exists()
                    if last_sub_record:
                        LoggingSubFunction.calculate_ending_balance_for_periodic(
                            last_period,
                            12,
                            stock_obj.tenant,
                            stock_obj.company
                        )
                else:
                    last_sub_record = ReportInventoryProductWarehouse.objects.filter(
                        period_mapped=period_obj,
                        sub_period_order=int(sub_period_order) - 1,
                        periodic_closed=False
                    ).exists()
                    if last_sub_record:
                        LoggingSubFunction.calculate_ending_balance_for_periodic(
                            period_obj,
                            int(sub_period_order) - 1,
                            stock_obj.tenant,
                            stock_obj.company
                        )

            new_log_list = cls.create_new_log_list(
                stock_obj,
                stock_data,
                period_obj,
                sub_period_order,
                config_inventory_management
            )
            for log in new_log_list:
                cls.update_current_value_dict_for_log(
                    log,
                    period_obj,
                    sub_period_order,
                    config_inventory_management
                )
            return True
        raise serializers.ValidationError(
            {'Period missing': f'Period of fiscal year {stock_obj_date.year} does not exist.'}
        )

    @classmethod
    def create_new_log_list(cls, stock_obj, stock_data, period_obj, sub_period_order, config_inventory_management):
        """ Step 1: Hàm tạo các log mới """
        bulk_info = []
        log_order_number = 0
        for item in stock_data:
            kw_parameter = {}
            if 1 in config_inventory_management:
                kw_parameter['warehouse_id'] = item['warehouse'].id
            if 2 in config_inventory_management:
                kw_parameter['lot_mapped_id'] = item['lot_data']['lot_id'] if len(item.get('lot_data')) > 0 else None
            if 3 in config_inventory_management:
                kw_parameter['sale_order_id'] = item['sale_order'].id if item.get('sale_order') else None

            if len(item.get('lot_data', {})) == 0:
                rp_inventory = ReportInventory.get_report_inventory(
                    stock_obj.tenant,
                    stock_obj.company,
                    stock_obj.employee_created,
                    stock_obj.employee_inherit,
                    period_obj,
                    sub_period_order,
                    item['product'],
                    **kw_parameter
                )
                cost = LoggingSubFunction.get_latest_log_value_dict(
                    stock_obj.company.company_config.definition_inventory_valuation,
                    item['product'].id,
                    **kw_parameter
                )['cost'] if item['stock_type'] == -1 else item['cost']
                new_log = cls(
                    tenant=stock_obj.tenant,
                    company=stock_obj.company,
                    employee_created=stock_obj.employee_created
                    if stock_obj.employee_created else stock_obj.employee_inherit,
                    employee_inherit=stock_obj.employee_inherit
                    if stock_obj.employee_inherit else stock_obj.employee_created,
                    report_inventory=rp_inventory,
                    product=item['product'],
                    sale_order=item.get('sale_order'),
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
                    lot_data=item.get('lot_data', {}),
                    log_order=log_order_number,
                    **kw_parameter
                )
                bulk_info.append(new_log)
                log_order_number += 1
            else:
                lot_data = item.get('lot_data', {})
                rp_inventory = ReportInventory.get_report_inventory(
                    stock_obj.tenant,
                    stock_obj.company,
                    stock_obj.employee_created,
                    stock_obj.employee_inherit,
                    period_obj,
                    sub_period_order,
                    item['product'],
                    **kw_parameter
                )
                cost = LoggingSubFunction.get_latest_log_value_dict(
                    stock_obj.company.company_config.definition_inventory_valuation,
                    item['product'].id,
                    **kw_parameter
                )['cost'] if item['stock_type'] == -1 else item['cost']

                lot_data['lot_value'] = cost * item['quantity']  # update value vao Lot
                new_log = cls(
                    tenant=stock_obj.tenant,
                    company=stock_obj.company,
                    employee_created=stock_obj.employee_created
                    if stock_obj.employee_created else stock_obj.employee_inherit,
                    employee_inherit=stock_obj.employee_inherit
                    if stock_obj.employee_inherit else stock_obj.employee_created,
                    report_inventory=rp_inventory,
                    product=item['product'],
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
                    lot_data=lot_data,
                    log_order=log_order_number,
                    **kw_parameter
                )
                bulk_info.append(new_log)
                log_order_number += 1
        new_log_list = cls.objects.bulk_create(bulk_info)
        return new_log_list

    @classmethod
    def update_current_value_dict_for_log(cls, log, period_obj, sub_period_order, config_inventory_management):
        """ Step 2: Hàm để cập nhập giá trị tồn kho khi log được ghi vào """
        div = log.company.company_config.definition_inventory_valuation
        kw_parameter = {}
        if 1 in config_inventory_management:
            kw_parameter['warehouse_id'] = log.warehouse_id
        if 2 in config_inventory_management:
            kw_parameter['lot_mapped_id'] = log.lot_mapped_id
        if 3 in config_inventory_management:
            kw_parameter['sale_order_id'] = log.sale_order_id

        if div == 0:
            # lấy value list của log gần nhất (nếu k, lấy số dư đầu kì)
            latest_value_dict = LoggingSubFunction.get_latest_log_value_dict(
                div,
                log.product_id,
                **kw_parameter
            )
            # tính toán value list mới
            new_value_list = LoggingSubFunction.calculate_new_value_dict_in_perpetual_inventory(
                log,
                latest_value_dict
            )
            # cập nhập giá trị tồn kho hiện tại mới cho log
            if new_value_list['quantity'] > 0:
                log.current_quantity = new_value_list['quantity']
                log.current_cost = new_value_list['cost']
                log.current_value = new_value_list['value']
            else:
                log.current_quantity = 0
                log.current_cost = 0
                log.current_value = 0
            log.save(update_fields=['current_quantity', 'current_cost', 'current_value'])
            cls.update_this_record_value_dict(
                log,
                period_obj,
                sub_period_order,
                latest_value_dict,
                div,
                **kw_parameter
            )
            return True
        if div == 1:
            # lấy value list của log gần nhất (nếu k, lấy số dư đầu kì)
            latest_value_dict = LoggingSubFunction.get_latest_log_value_dict(
                div,
                log.product_id,
                **kw_parameter
            )
            # tính toán value list mới
            new_value_list = LoggingSubFunction.calculate_new_value_dict_in_periodic_inventory(
                log,
                latest_value_dict
            )
            # cập nhập giá trị tồn kho hiện tại mới cho log
            # chỗ này k cần check SL = 0 -> cost = 0 vì mọi TH cost đều = 0
            log.periodic_current_quantity = new_value_list['quantity']
            log.periodic_current_cost = new_value_list['cost']  # = 0
            log.periodic_current_value = new_value_list['value']  # = 0
            log.save(update_fields=['periodic_current_quantity', 'periodic_current_cost', 'periodic_current_value'])
            cls.update_this_record_value_dict(
                log,
                period_obj,
                sub_period_order,
                latest_value_dict,
                div,
                **kw_parameter
            )
            return True
        raise serializers.ValidationError({'Company config': 'Company inventory valuation config must be 0 or 1.'})

    @classmethod
    def update_this_record_value_dict_for_periodic_inventory(
        cls, this_rp_prd_wh, log, period_obj, sub_period_order, latest_value_dict, **kwargs
    ):
        # nếu kiểm kê định kì
        if not this_rp_prd_wh:  # nếu không có thì tạo, gán log
            this_rp_prd_wh = ReportInventoryProductWarehouse.objects.create(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                employee_created=log.employee_created,
                employee_inherit=log.employee_inherit if log.employee_inherit else log.employee_created,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                opening_balance_quantity=latest_value_dict['quantity'],
                opening_balance_cost=latest_value_dict['cost'],
                opening_balance_value=latest_value_dict['value'],
                periodic_ending_balance_quantity=log.current_quantity,
                periodic_ending_balance_cost=log.current_cost,
                periodic_ending_balance_value=log.current_value,
                sub_latest_log=log,
                **kwargs
            )
        else:  # có thì update giá cost, gán sub
            this_rp_prd_wh.periodic_ending_balance_quantity = log.periodic_current_quantity
            this_rp_prd_wh.periodic_ending_balance_cost = log.periodic_current_cost
            this_rp_prd_wh.periodic_ending_balance_value = log.periodic_current_value
            this_rp_prd_wh.sub_latest_log = log
            # nếu kì đã đóng mà có giao dịch, mở lại, cost-value hiện tại trở về 0 (chưa chốt)
            if this_rp_prd_wh.periodic_closed:
                this_rp_prd_wh.periodic_closed = False
                this_rp_prd_wh.periodic_ending_balance_cost = 0
                this_rp_prd_wh.periodic_ending_balance_value = 0

        if log.stock_type == 1:
            # nếu là input thì cộng tổng SL nhập và tổng Value nhập
            this_rp_prd_wh.sum_input_quantity += log.quantity
            this_rp_prd_wh.sum_input_value += log.quantity * log.cost
        else:
            # nếu là xuất thì cập nhập SL xuất
            this_rp_prd_wh.sum_output_quantity += log.quantity
            this_rp_prd_wh.sum_output_quantity += log.quantity
        this_rp_prd_wh.save(update_fields=[
            'sum_input_quantity',
            'sum_input_value',
            'sum_output_quantity',
            'sum_output_value',
            'sub_latest_log',
            'periodic_ending_balance_quantity',
            'periodic_ending_balance_cost',
            'periodic_ending_balance_value',
            'periodic_closed'
        ])

    @classmethod
    def update_this_record_value_dict_for_perpetual_inventory(
        cls, this_rp_prd_wh, log, period_obj, sub_period_order, latest_value_dict, **kwargs
    ):
        if not this_rp_prd_wh:  # không có thì tạo, gán log
            this_rp_prd_wh = ReportInventoryProductWarehouse.objects.create(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                employee_created=log.employee_created,
                employee_inherit=log.employee_inherit if log.employee_inherit else log.employee_created,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                opening_balance_quantity=latest_value_dict['quantity'],
                opening_balance_cost=latest_value_dict['cost'],
                opening_balance_value=latest_value_dict['value'],
                ending_balance_quantity=log.current_quantity,
                ending_balance_cost=log.current_cost,
                ending_balance_value=log.current_value,
                sub_latest_log=log,
                **kwargs
            )
        else:  # nếu có thì update giá cost, gán sub
            this_rp_prd_wh.ending_balance_quantity = log.current_quantity
            this_rp_prd_wh.ending_balance_cost = log.current_cost
            this_rp_prd_wh.ending_balance_value = log.current_value
            this_rp_prd_wh.sub_latest_log = log

        if log.stock_type == 1:
            # nếu là input thì cộng tổng SL nhập và tổng Value nhập
            this_rp_prd_wh.sum_input_quantity += log.quantity
            this_rp_prd_wh.sum_input_value += log.quantity * log.cost
        else:
            # nếu là xuất thì cập nhập SL xuất
            this_rp_prd_wh.sum_output_quantity += log.quantity
            this_rp_prd_wh.sum_output_value += log.quantity * log.cost
        this_rp_prd_wh.save(update_fields=[
            'sum_input_quantity',
            'sum_input_value',
            'sum_output_quantity',
            'sum_output_value',
            'ending_balance_quantity',
            'ending_balance_cost',
            'ending_balance_value',
            'sub_latest_log'
        ])

    @classmethod
    def update_this_record_value_dict(cls, log, period_obj, sub_period_order, latest_value_dict, div, **kwargs):
        """
        Step 3: Hàm kiểm tra record quản lí giá cost của sp theo từng kho trong kì nay đã có hay chưa ?
        Chưa thì tạo mới - Có thì Update lại quantity-cost-value
        """
        sub_period_obj = period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            # tìm record
            this_record = ReportInventoryProductWarehouse.objects.filter(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                **kwargs
            ).first()

            # nếu kiểm kê thường xuyên
            if div == 0:
                cls.update_this_record_value_dict_for_perpetual_inventory(
                    this_record,
                    log,
                    period_obj,
                    sub_period_order,
                    latest_value_dict,
                    **kwargs
                )
            else:
                cls.update_this_record_value_dict_for_periodic_inventory(
                    this_record,
                    log,
                    period_obj,
                    sub_period_order,
                    latest_value_dict,
                    **kwargs
                )

            # cập nhập log mới nhất, không có thì tạo mới
            latest_log_obj = log.product.latest_log_product.filter(**kwargs).first()
            if latest_log_obj:
                latest_log_obj.latest_log = log
                latest_log_obj.save(update_fields=['latest_log'])
            else:
                latest_log_obj = LatestSub.objects.create(
                    product=log.product,
                    latest_log=log,
                    **kwargs
                )

            return this_record
        raise serializers.ValidationError({'Sub period missing': 'Sub period of this period does not exist.'})

    class Meta:
        verbose_name = 'Report Inventory By Month'
        verbose_name_plural = 'Report Inventory By Months'
        ordering = ('-system_date',)
        default_permissions = ()
        permissions = ()


class ReportInventoryProductWarehouse(DataAbstractModel):  # rp_prd_wh
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
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='report_inventory_product_warehouse_lot_mapped',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_inventory_product_warehouse_sale_order",
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

    # periodic_adjustment_ending_quantity = models.FloatField(default=0)
    # ia_item_mapped = models.ForeignKey(
    #     'inventory.InventoryAdjustmentItem',
    #     on_delete=models.SET_NULL,
    #     related_name='periodic_ia_item_mapped',
    #     null=True
    # )

    sum_input_quantity = models.FloatField(default=0)
    sum_input_value = models.FloatField(default=0)
    sum_output_quantity = models.FloatField(default=0)
    sum_output_value = models.FloatField(default=0)

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
        null=True
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='latest_log_lot_mapped',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="latest_log_sale_order",
        null=True
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
    def get_latest_log(cls, product_id, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm lấy Log gần nhất theo sp và kho. Không có trả về None
        """
        last_record = LatestSub.objects.filter(
            product_id=product_id,
            **kwargs
        ).first()
        return last_record.latest_log if last_record else None

    @classmethod
    def get_latest_log_by_month(cls, period_obj, sub_period_order, product_id, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm để lấy Log cuối cùng của tháng trước theo sp và kho. Truyền vào tham số tháng này
        """
        if int(sub_period_order) == 1:
            last_rp_prd_wh = ReportInventoryProductWarehouse.objects.filter(
                product_id=product_id,
                period_mapped__fiscal_year=period_obj.fiscal_year - 1,
                sub_period_order=12,
                **kwargs
            ).first()
        else:
            last_rp_prd_wh = ReportInventoryProductWarehouse.objects.filter(
                product_id=product_id,
                period_mapped=period_obj,
                sub_period_order=int(sub_period_order) - 1,
                **kwargs
            ).first()
        return last_rp_prd_wh.sub_latest_log if last_rp_prd_wh else None

    @classmethod
    def get_latest_log_value_dict(cls, div, product_id, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm tìm value_dict Log gần nhất, không có trả về đầu kỳ hiện tại
        """
        latest_trans = LoggingSubFunction.get_latest_log(
            product_id,
            **kwargs
        )
        if latest_trans:
            return {
                'quantity': latest_trans.current_quantity,
                'cost': latest_trans.current_cost,
                'value': latest_trans.current_value
            } if div == 0 else {
                'quantity': latest_trans.periodic_current_quantity,
                'cost': 0,
                'value': 0
            }
        return cls.get_opening_balance_value_dict(
            product_id,
            3,
            **kwargs
        )

    @classmethod
    def calculate_new_value_dict_in_perpetual_inventory(cls, log, latest_value_dict):
        """ Hàm tính toán cho Phương pháp Kê khai thường xuyên """
        if log.stock_type == 1:
            new_quantity = latest_value_dict['quantity'] + log.quantity
            sum_value = latest_value_dict['value'] + log.value
            new_cost = (sum_value / new_quantity) if new_quantity else 0
            new_value = sum_value
        else:
            new_quantity = latest_value_dict['quantity'] - log.quantity
            new_cost = latest_value_dict['cost']
            new_value = new_cost * new_quantity
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def calculate_new_value_dict_in_periodic_inventory(cls, log, latest_value_dict):
        """ Hàm tính toán cho Phương pháp Kiểm kê định kì """
        if log.stock_type == 1:
            # Lúc này sum nhập đã được cập nhập
            new_quantity = latest_value_dict['quantity'] + log.quantity
            new_cost = 0
            new_value = 0
        else:
            new_quantity = latest_value_dict['quantity'] - log.quantity
            new_cost = 0
            new_value = 0
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def get_opening_balance_value_dict(cls, product_id, data_type=1, **kwargs):
        """
        * kwargs_format:
        - required: []
        - option 1: [warehouse_id]
        Hàm để lấy Số dư đầu kì theo SP và KHO
        (0-quantity, 1-cost, 2-value, 3-{'quantity':, 'cost':, 'value':}, else-return1)
        """
        # tìm số dư đầu kì
        this_record = ReportInventoryProductWarehouse.objects.filter(
            product_id=product_id,
            for_balance=True,
            **kwargs
        ).first()
        if this_record:
            if data_type == 0:
                return this_record.opening_balance_quantity
            if data_type == 1:
                return this_record.opening_balance_cost
            if data_type == 2:
                return this_record.opening_balance_value
            if data_type == 3:
                return {
                    'quantity': this_record.opening_balance_quantity,
                    'cost': this_record.opening_balance_cost,
                    'value': this_record.opening_balance_value
                }
            return this_record.opening_balance_cost
        return 0 if data_type != 3 else {'quantity': 0, 'cost': 0, 'value': 0}

    @classmethod
    def get_balance_data_this_sub(cls, this_rp_prd_wh):
        """
        Hàm lấy opening và ending của kỳ này
        """
        # Begin get Opening
        opening_quantity = this_rp_prd_wh.opening_balance_quantity
        opening_cost = this_rp_prd_wh.opening_balance_cost
        opening_value = this_rp_prd_wh.opening_balance_value
        # End

        # Begin get Ending
        if this_rp_prd_wh.sub_latest_log:
            if this_rp_prd_wh.company.company_config.definition_inventory_valuation == 0:
                ending_quantity = this_rp_prd_wh.sub_latest_log.current_quantity
                ending_cost = this_rp_prd_wh.sub_latest_log.current_cost
                ending_value = this_rp_prd_wh.sub_latest_log.current_value
            else:
                ending_quantity = this_rp_prd_wh.periodic_ending_balance_quantity
                ending_cost = this_rp_prd_wh.periodic_ending_balance_cost
                ending_value = this_rp_prd_wh.periodic_ending_balance_value
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
    def calculate_ending_balance_for_periodic(cls, period_obj, sub_period_order, tenant, company):
        for this_record in ReportInventoryProductWarehouse.objects.filter(
                tenant=tenant,
                company=company,
                period_mapped=period_obj,
                sub_period_order=sub_period_order
        ):
            sum_input_quantity = this_record.sum_input_quantity
            sum_input_value = this_record.sum_input_value
            sum_output_quantity = this_record.sum_output_quantity

            if sum_input_quantity > 0:
                quantity = sum_input_quantity - sum_output_quantity
                cost = (sum_input_value / sum_input_quantity) if sum_input_quantity > 0 else 0
                value = quantity * cost
            else:
                quantity = this_record.opening_balance_quantity
                cost = this_record.opening_balance_cost
                value = this_record.opening_balance_value

            value_list = {'quantity': quantity, 'cost': cost, 'value': value}
            if value_list['quantity'] > 0:
                this_record.periodic_ending_balance_quantity = value_list['quantity']
                this_record.periodic_ending_balance_cost = value_list['cost']
                this_record.periodic_ending_balance_value = value_list['value']
            else:
                this_record.periodic_ending_balance_quantity = 0
                this_record.periodic_ending_balance_cost = 0
                this_record.periodic_ending_balance_value = 0
            this_record.periodic_closed = True
            this_record.save(update_fields=[
                'periodic_ending_balance_quantity',
                'periodic_ending_balance_cost',
                'periodic_ending_balance_value',
                'periodic_closed'
            ])
        return True
