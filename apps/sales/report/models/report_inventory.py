from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import Periods
from apps.sales.inventory.models.goods_registration import GoodsRegistration
from apps.shared import DataAbstractModel, SimpleAbstractModel


class ReportStock(DataAbstractModel):  # rp_stock
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_stock_product',
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='report_stock_lot_mapped',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_stock_sale_order",
        null=True
    )

    period_mapped = models.ForeignKey(
        'saledata.Periods',
        on_delete=models.CASCADE,
        related_name='report_stock_period_mapped',
        null=True,
    )

    sub_period_order = models.IntegerField()
    sub_period = models.ForeignKey(
        'saledata.SubPeriods',
        on_delete=models.CASCADE,
        related_name='report_stock_sub_period',
        null=True,
    )

    @classmethod
    def get_report_stock(
            cls, tenant_obj, company_obj, emp_created_obj, emp_inherit_obj, period_obj, sub_period_order,
            product_obj, **kwargs
    ):
        if 'warehouse_id' in kwargs:
            del kwargs['warehouse_id']
        sub_period_obj = period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            rp_stock, _created = cls.objects.get_or_create(
                tenant=tenant_obj,
                company=company_obj,
                product=product_obj,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                defaults={
                    'employee_created': emp_created_obj if emp_created_obj else emp_inherit_obj,
                    'employee_inherit': emp_inherit_obj if emp_inherit_obj else emp_created_obj,
                    **kwargs
                }
            )
            return rp_stock
        raise serializers.ValidationError({'Sub period missing': 'Sub period object does not exist.'})

    class Meta:
        verbose_name = 'Report Stock'
        verbose_name_plural = 'Report Stocks'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()


class ReportStockLog(DataAbstractModel):  # rp_log
    report_stock = models.ForeignKey(
        ReportStock,
        on_delete=models.CASCADE,
        related_name='report_stock_log',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_stock_log_product'
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='report_stock_log_lot_mapped',
        null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_stock_log_warehouse',
        null=True
    )
    physical_warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_stock_log_physical_warehouse',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_stock_log_sale_order",
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
        print('---get_config_inventory_management')
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
        print('---cast_quantity_to_unit')
        return log_quantity * log_uom.ratio

    @classmethod
    def logging_inventory_activities(cls, stock_obj, stock_obj_date, stock_data):
        print('---logging_inventory_activities')
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
                    last_period_obj = Periods.objects.filter(
                        tenant=stock_obj.tenant,
                        company=stock_obj.company,
                        fiscal_year=period_obj.fiscal_year - 1
                    ).first()
                    pre_rp_inventory_cost_obj = ReportInventoryCost.objects.filter(
                        period_mapped=last_period_obj,
                        sub_period_order=12,
                        periodic_closed=False
                    ).exists()
                    if pre_rp_inventory_cost_obj:
                        ReportInventorySubFunction.calculate_ending_balance_for_periodic(
                            last_period_obj,
                            12,
                            stock_obj.tenant,
                            stock_obj.company
                        )
                else:
                    pre_rp_inventory_cost_obj = ReportInventoryCost.objects.filter(
                        period_mapped=period_obj,
                        sub_period_order=int(sub_period_order) - 1,
                        periodic_closed=False
                    ).exists()
                    if pre_rp_inventory_cost_obj:
                        ReportInventorySubFunction.calculate_ending_balance_for_periodic(
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
                cls.update_current_value_for_log(
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
        print('---create_new_log_list')
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

            rp_inventory = ReportStock.get_report_stock(
                stock_obj.tenant,
                stock_obj.company,
                stock_obj.employee_created,
                stock_obj.employee_inherit,
                period_obj,
                sub_period_order,
                item['product'],
                **kw_parameter
            )
            item['cost'] = ReportInventorySubFunction.get_latest_log_value_dict(
                stock_obj.company.company_config.definition_inventory_valuation,
                item['product'].id,
                item['warehouse'].id,
                **kw_parameter
            )['cost'] if item['stock_type'] == -1 else item['cost']

            item['value'] = item['cost'] * item['quantity']
            if len(item.get('lot_data', {})) != 0:
                item['lot_data']['lot_value'] = item['cost'] * item['quantity']  # update value vao Lot
            new_log = cls(
                tenant=stock_obj.tenant,
                company=stock_obj.company,
                employee_created=stock_obj.employee_created
                if stock_obj.employee_created else stock_obj.employee_inherit,
                employee_inherit=stock_obj.employee_inherit
                if stock_obj.employee_inherit else stock_obj.employee_created,
                report_stock=rp_inventory,
                product=item['product'],
                physical_warehouse=item['warehouse'],
                sale_order=item.get('sale_order'),
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
                lot_data=item.get('lot_data', {}),
                log_order=log_order_number,
                **kw_parameter
            )
            bulk_info.append(new_log)
            log_order_number += 1

            if 'sale_order_id' in kw_parameter:  # Project
                ReportInventorySubFunction.regis_stock(stock_obj, item)

        return cls.objects.bulk_create(bulk_info)

    @classmethod
    def update_current_value_for_log(cls, log, period_obj, sub_period_order, config_inventory_management):
        print('---update_current_value_for_log')
        """ Step 2: Hàm để cập nhập giá trị tồn kho khi log được ghi vào """
        div = log.company.company_config.definition_inventory_valuation
        kw_parameter = {}
        if 1 in config_inventory_management:
            kw_parameter['warehouse_id'] = log.warehouse_id
        if 2 in config_inventory_management:
            kw_parameter['lot_mapped_id'] = log.lot_mapped_id
        if 3 in config_inventory_management:
            kw_parameter['sale_order_id'] = log.sale_order_id

        # lấy value list của log gần nhất (nếu k, lấy số dư đầu kì)
        latest_value_dict = ReportInventorySubFunction.get_latest_log_value_dict(
            div,
            log.product_id,
            log.warehouse_id if log.warehouse_id else log.physical_warehouse_id,
            **kw_parameter
        )

        if div == 0:
            new_value_dict = ReportInventorySubFunction.calculate_new_value_dict_in_perpetual(
                log, latest_value_dict
            )
            # cập nhập giá trị tồn kho hiện tại mới cho log
            log.current_quantity, log.current_cost, log.current_value = (
                new_value_dict['quantity'], new_value_dict['cost'], new_value_dict['value']
            ) if new_value_dict['quantity'] > 0 else (0, 0, 0)
            log.save(update_fields=['current_quantity', 'current_cost', 'current_value'])
        if div == 1:
            new_value_dict = ReportInventorySubFunction.calculate_new_value_dict_in_periodic(
                log, latest_value_dict
            )
            # cập nhập giá trị tồn kho hiện tại mới cho log
            # chỗ này k cần check SL = 0 -> cost = 0 vì mọi TH cost đều = 0
            log.periodic_current_quantity, log.periodic_current_cost, log.periodic_current_value = (
                new_value_dict['quantity'], new_value_dict['cost'], new_value_dict['value']
            )
            log.save(update_fields=['periodic_current_quantity', 'periodic_current_cost', 'periodic_current_value'])

        return cls.update_this_rp_inventory_cost_value_dict(
            log, period_obj, sub_period_order, latest_value_dict['cost'], div, **kw_parameter
        )

    @classmethod
    def create_or_update_current_value_for_perpetual(
        cls, this_rp_inventory_cost, log, period_obj, sub_period_order, latest_value_dict, **kwargs
    ):
        print('---create_or_update_current_value_for_perpetual')
        ending_balance_quantity = latest_value_dict['quantity'] + (log.quantity * log.stock_type)
        if not this_rp_inventory_cost:  # không có thì tạo, gán log
            this_rp_inventory_cost = ReportInventoryCost.objects.create(
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
                ending_balance_quantity=ending_balance_quantity,
                ending_balance_cost=log.current_cost,
                ending_balance_value=ending_balance_quantity * log.current_cost,
                sub_latest_log=log,
                **kwargs
            )
        else:  # nếu có thì update giá cost, gán sub
            this_rp_inventory_cost.ending_balance_quantity = ending_balance_quantity
            this_rp_inventory_cost.ending_balance_cost = log.current_cost
            this_rp_inventory_cost.ending_balance_value = ending_balance_quantity * log.current_cost
            this_rp_inventory_cost.sub_latest_log = log

        if log.stock_type == 1:
            # nếu là input thì cộng tổng SL nhập và tổng Value nhập
            this_rp_inventory_cost.sum_input_quantity += log.quantity
            this_rp_inventory_cost.sum_input_value += log.quantity * log.cost
        else:
            # nếu là xuất thì cập nhập SL xuất
            this_rp_inventory_cost.sum_output_quantity += log.quantity
            this_rp_inventory_cost.sum_output_value += log.quantity * log.cost
        this_rp_inventory_cost.save(update_fields=[
            'sum_input_quantity',
            'sum_input_value',
            'sum_output_quantity',
            'sum_output_value',
            'ending_balance_quantity',
            'ending_balance_cost',
            'ending_balance_value',
            'sub_latest_log'
        ])
        return this_rp_inventory_cost

    @classmethod
    def create_or_update_current_value_for_periodic(
        cls, this_rp_inventory_cost, log, period_obj, sub_period_order, latest_value_dict, **kwargs
    ):
        print('---create_or_update_current_value_for_periodic')
        ending_balance_quantity = latest_value_dict['quantity'] + (log.quantity * log.stock_type)
        if not this_rp_inventory_cost:
            this_rp_inventory_cost = ReportInventoryCost.objects.create(
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
                periodic_ending_balance_quantity=ending_balance_quantity,
                periodic_ending_balance_cost=log.current_cost,
                periodic_ending_balance_value=ending_balance_quantity * log.current_cost,
                sub_latest_log=log,
                **kwargs
            )
        else:  # có thì update giá cost, gán sub
            this_rp_inventory_cost.periodic_ending_balance_quantity = ending_balance_quantity
            this_rp_inventory_cost.periodic_ending_balance_cost = log.current_cost
            this_rp_inventory_cost.periodic_ending_balance_value = ending_balance_quantity * log.current_cost
            this_rp_inventory_cost.sub_latest_log = log
            # nếu kì đã đóng mà có giao dịch, mở lại, cost-value hiện tại trở về 0 (chưa chốt)
            if this_rp_inventory_cost.periodic_closed:
                this_rp_inventory_cost.periodic_closed = False
                this_rp_inventory_cost.periodic_ending_balance_cost = 0
                this_rp_inventory_cost.periodic_ending_balance_value = 0

        if log.stock_type == 1:
            # nếu là input thì cộng tổng SL nhập và tổng Value nhập
            this_rp_inventory_cost.sum_input_quantity += log.quantity
            this_rp_inventory_cost.sum_input_value += log.quantity * log.cost
        else:
            # nếu là xuất thì cập nhập SL xuất
            this_rp_inventory_cost.sum_output_quantity += log.quantity
            this_rp_inventory_cost.sum_output_quantity += log.quantity
        this_rp_inventory_cost.save(update_fields=[
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
        return this_rp_inventory_cost

    @classmethod
    def update_this_rp_inventory_cost_value_dict(
            cls, log, period_obj, sub_period_order, latest_cost, div, **kwargs
    ):
        print('---update_this_rp_inventory_cost_value_dict')
        """
        Step 3: Hàm kiểm tra record cost của sp này trong kì nay đã có hay chưa ?
                Chưa thì tạo mới - Có thì Update lại quantity-cost-value
        """
        sub_period_obj = period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            sum_ending_balance_quantity = 0
            for record in LatestLog.objects.filter(product_id=log.product_id, **kwargs):
                sum_ending_balance_quantity += record.latest_log.current_quantity
            latest_value_dict = {
                'quantity': sum_ending_balance_quantity,
                'cost': latest_cost,
                'value': sum_ending_balance_quantity * latest_cost
            }

            this_rp_inventory_cost = ReportInventoryCost.objects.filter(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                **kwargs
            ).first()

            this_rp_inventory_cost = cls.create_or_update_current_value_for_perpetual(
                this_rp_inventory_cost, log, period_obj, sub_period_order, latest_value_dict, **kwargs
            ) if div == 0 else cls.create_or_update_current_value_for_periodic(
                this_rp_inventory_cost, log, period_obj, sub_period_order, latest_value_dict, **kwargs
            )

            if 'sale_order_id' in kwargs:  # Project
                this_rp_inventory_cost_wh = this_rp_inventory_cost.report_inventory_cost_wh.filter(
                    warehouse=log.physical_warehouse
                ).first()
                if this_rp_inventory_cost_wh:
                    this_rp_inventory_cost_wh.ending_quantity += log.quantity * log.stock_type
                    this_rp_inventory_cost_wh.save(update_fields=['ending_quantity'])
                else:
                    previous_ending_quantity = ReportInventoryCostWH.get_project_previous_ending_quantity(
                        this_rp_inventory_cost, log.physical_warehouse
                    )
                    ReportInventoryCostWH.objects.create(
                        report_inventory_cost=this_rp_inventory_cost,
                        warehouse=log.physical_warehouse,
                        opening_quantity=previous_ending_quantity,
                        ending_quantity=previous_ending_quantity + log.quantity * log.stock_type
                    )

            # cập nhập log mới nhất, không có thì tạo mới
            latest_log_obj = log.product.latest_log_product.filter(
                warehouse_id=log.physical_warehouse_id, **kwargs
            ).first() if 'warehouse_id' not in kwargs else log.product.latest_log_product.filter(**kwargs).first()
            if latest_log_obj:
                latest_log_obj.latest_log = log
                latest_log_obj.save(update_fields=['latest_log'])
            else:
                LatestLog.objects.create(product=log.product, latest_log=log, **kwargs)

            return True
        raise serializers.ValidationError({'Sub period missing': 'Sub period of this period does not exist.'})

    class Meta:
        verbose_name = 'Report Stock Log'
        verbose_name_plural = 'Report Stock Logs'
        ordering = ('-system_date',)
        default_permissions = ()
        permissions = ()


class ReportInventoryCost(DataAbstractModel):  # rp_inventory_cost
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_inventory_cost_product',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_inventory_cost_warehouse',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_inventory_cost_sale_order",
        null=True
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.SET_NULL,
        related_name='report_inventory_cost_lot_mapped',
        null=True
    )

    period_mapped = models.ForeignKey(
        'saledata.Periods',
        on_delete=models.CASCADE,
        related_name='report_inventory_cost_period_mapped',
        null=True,
    )
    sub_period_order = models.IntegerField()
    sub_period = models.ForeignKey(
        'saledata.SubPeriods',
        on_delete=models.CASCADE,
        related_name='report_inventory_cost_sub_period',
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
        ReportStockLog,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = 'Report Inventory Cost'
        verbose_name_plural = 'Report Inventory Costs'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ReportInventoryCostWH(SimpleAbstractModel):
    report_inventory_cost = models.ForeignKey(
        ReportInventoryCost,
        on_delete=models.CASCADE,
        related_name='report_inventory_cost_wh',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='report_inventory_cost_wh_warehouse',
        null=True
    )
    opening_quantity = models.FloatField(default=0)
    ending_quantity = models.FloatField(default=0)

    @classmethod
    def get_project_previous_ending_quantity(cls, report_inventory_cost, warehouse):
        print('---get_project_previous_ending_quantity')
        previous = cls.objects.filter(
            report_inventory_cost=report_inventory_cost,
            warehouse=warehouse
        ).order_by(
            '-report_inventory_cost__period_mapped__fiscal_year',
            '-report_inventory_cost__sub_period_order'
        ).first()
        return previous.ending_quantity if previous else 0

    class Meta:
        verbose_name = 'Report Inventory Cost WH'
        verbose_name_plural = 'Report Inventory Cost WH'
        ordering = ()
        default_permissions = ()
        permissions = ()


class LatestLog(SimpleAbstractModel):
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
        ReportStockLog,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = 'Latest Log'
        verbose_name_plural = 'Latest Log'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ReportInventorySubFunction:
    @classmethod
    def regis_stock(cls, stock_obj, stock_data_item):
        print('---regis_stock')
        if stock_data_item.get('trans_title') == 'Delivery':
            GoodsRegistration.update_registered_quantity(
                stock_obj.order_delivery.sale_order,
                stock_data_item,
                **{'delivery_id': stock_obj.id}
            )
        if stock_data_item.get('trans_title') == 'Goods receipt':
            for po_pr_mapped in stock_obj.purchase_order.purchase_order_request_order.all():
                sale_order = po_pr_mapped.purchase_request.sale_order
                if sale_order:
                    GoodsRegistration.update_registered_quantity(
                        sale_order, stock_data_item, **{'goods_receipt_id': stock_obj.id}
                    )
        return True

    @classmethod
    def get_latest_month_log(cls, period_obj, sub_period_order, product_id, **kwargs):
        print('---get_latest_month_log')
        latest_month_log = ReportInventoryCost.objects.filter(
            product_id=product_id,
            period_mapped__fiscal_year=period_obj.fiscal_year - 1,
            sub_period_order=12,
            **kwargs
        ).first() if int(sub_period_order) == 1 else ReportInventoryCost.objects.filter(
            product_id=product_id,
            period_mapped=period_obj,
            sub_period_order=int(sub_period_order) - 1,
            **kwargs
        ).first()
        return latest_month_log.sub_latest_log if latest_month_log else None

    @classmethod
    def get_latest_log_value_dict(cls, div, product_id, warehouse_id, **kwargs):
        print('---get_latest_log_value_dict')
        latest_log_record = LatestLog.objects.filter(
            product_id=product_id, warehouse_id=warehouse_id, **kwargs
        ).first()
        latest_log = latest_log_record.latest_log if latest_log_record else None
        if latest_log:
            return {
                'quantity': latest_log.current_quantity,
                'cost': latest_log.current_cost,
                'value': latest_log.current_value
            } if div == 0 else {
                'quantity': latest_log.periodic_current_quantity,
                'cost': 0,
                'value': 0
            }
        return cls.get_opening_balance_value_dict(product_id, warehouse_id, 3, **kwargs)

    @classmethod
    def calculate_new_value_dict_in_perpetual(cls, log, latest_value_dict):
        print('---calculate_new_value_dict_in_perpetual')
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
    def calculate_new_value_dict_in_periodic(cls, log, latest_value_dict):
        print('---calculate_new_value_dict_in_periodic')
        """ Hàm tính toán cho Phương pháp Kiểm kê định kì """
        # Lúc này sum nhập đã được cập nhập
        return {
            'quantity': latest_value_dict['quantity'] + (log.quantity * log.stock_type),
            'cost': 0,
            'value': 0
        }

    @classmethod
    def get_opening_balance_value_dict(cls, product_id, warehouse_id, data_type=1, **kwargs):
        print('---get_opening_balance_value_dict')
        """ Hàm tìm số dư đầu kì """
        this_record = ReportInventoryCost.objects.filter(
            product_id=product_id, warehouse_id=warehouse_id, for_balance=True, **kwargs
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
        return {'quantity': 0, 'cost': 0, 'value': 0}

    @classmethod
    def get_balance_data_this_sub_period(cls, this_rp_inventory_cost, warehouse_id=None):
        print('---get_balance_data_this_sub_period')
        """ Hàm lấy opening và ending của kỳ này """
        if not warehouse_id:
            # Get Opening
            opening_quantity = this_rp_inventory_cost.opening_balance_quantity
            opening_cost = this_rp_inventory_cost.opening_balance_cost
            opening_value = this_rp_inventory_cost.opening_balance_value

            # Get Ending
            ending_quantity, ending_cost, ending_value = (
                this_rp_inventory_cost.ending_balance_quantity,
                this_rp_inventory_cost.ending_balance_cost,
                this_rp_inventory_cost.ending_balance_value
            ) if this_rp_inventory_cost.company.company_config.definition_inventory_valuation == 0 else (
                this_rp_inventory_cost.periodic_ending_balance_quantity,
                this_rp_inventory_cost.periodic_ending_balance_cost,
                this_rp_inventory_cost.periodic_ending_balance_value
            )
        else:
            this_rp_inventory_cost_wh = this_rp_inventory_cost.report_inventory_cost_wh.filter(
                warehouse_id=warehouse_id
            ).first()
            if this_rp_inventory_cost_wh:
                # Get Opening
                opening_quantity = this_rp_inventory_cost_wh.opening_quantity
                opening_cost = this_rp_inventory_cost.opening_balance_cost
                opening_value = opening_quantity * opening_cost

                # Get Ending
                ending_quantity, ending_cost, ending_value = (
                    this_rp_inventory_cost_wh.ending_quantity,
                    this_rp_inventory_cost.ending_balance_cost,
                    this_rp_inventory_cost_wh.ending_quantity * this_rp_inventory_cost.ending_balance_cost
                ) if this_rp_inventory_cost.company.company_config.definition_inventory_valuation == 0 else (
                    this_rp_inventory_cost.periodic_ending_balance_quantity,
                    this_rp_inventory_cost.periodic_ending_balance_cost,
                    this_rp_inventory_cost.periodic_ending_balance_value
                )
            else:
                (
                    opening_quantity, opening_cost, opening_value, ending_quantity, ending_cost, ending_value
                ) = 0, 0, 0, 0, 0, 0

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
        print('---calculate_ending_balance_for_periodic')
        for this_rp_inventory_cost in ReportInventoryCost.objects.filter(
            tenant=tenant, company=company, period_mapped=period_obj, sub_period_order=sub_period_order
        ):
            sum_input_quantity = this_rp_inventory_cost.sum_input_quantity
            sum_input_value = this_rp_inventory_cost.sum_input_value
            sum_output_quantity = this_rp_inventory_cost.sum_output_quantity

            quantity, cost, value = (
                sum_input_quantity - sum_output_quantity,
                (sum_input_value / sum_input_quantity) if sum_input_quantity > 0 else 0,
                sum_input_quantity - sum_output_quantity * (
                        sum_input_value / sum_input_quantity
                ) if sum_input_quantity > 0 else 0
            ) if sum_input_quantity > 0 else (
                this_rp_inventory_cost.opening_balance_quantity,
                this_rp_inventory_cost.opening_balance_cost,
                this_rp_inventory_cost.opening_balance_value
            )

            (
                this_rp_inventory_cost.periodic_ending_balance_quantity,
                this_rp_inventory_cost.periodic_ending_balance_cost,
                this_rp_inventory_cost.periodic_ending_balance_value
            ) = (quantity, cost, value) if quantity > 0 else (0, 0, 0)

            this_rp_inventory_cost.periodic_closed = True
            this_rp_inventory_cost.save(
                update_fields=[
                    'periodic_ending_balance_quantity',
                    'periodic_ending_balance_cost',
                    'periodic_ending_balance_value',
                    'periodic_closed'
                ]
            )
        return True
