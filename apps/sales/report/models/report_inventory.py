from django.db import models
from rest_framework import serializers
from apps.sales.inventory.models.goods_registration import GoodsRegistration
from apps.shared import DataAbstractModel, SimpleAbstractModel


# - ReportStock: lưu sản phẩm theo từng tháng trong năm tài chính.
# - ReportStockLog: lưu quá trình nhập xuất kho và giá cost của sản phẩm sau mỗi lần nhập
# - ReportInventoryCost: lưu giá cost đầu kì và cuối kì (hiện tại) của sản phẩm theo từng tháng trong năm tài chính
# - ReportInventoryCostByWarehouse: lưu kho vật lí của sản phẩm (cho TH tính cost theo dự án)
# - ReportInventoryCostLatestLog: lưu giao dịch gần nhất của sản phẩm

class BalanceInitialization(DataAbstractModel):
    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE)
    uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    value = models.FloatField(default=0)
    data_lot = models.JSONField(default=list)
    data_sn = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Balance Initialization'
        verbose_name_plural = 'Balance Initialization'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()


class BalanceInitializationLot(DataAbstractModel):
    balance_init = models.ForeignKey(BalanceInitialization, on_delete=models.CASCADE)
    lot_mapped = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Balance Initialization Lot'
        verbose_name_plural = 'Balance Initialization Lots'
        ordering = ()
        default_permissions = ()
        permissions = ()


class BalanceInitializationSerial(DataAbstractModel):
    balance_init = models.ForeignKey(BalanceInitialization, on_delete=models.CASCADE)
    serial_mapped = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Balance Initialization Serial'
        verbose_name_plural = 'Balance Initialization Serials'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ReportStock(DataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='report_stock_product',
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        related_name='report_stock_lot_mapped',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_stock_sale_order",
        null=True
    )
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        related_name="report_stock_lease_order",
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
    def get_or_create_report_stock(cls, doc_obj, period_obj, sub_period_order, product_obj, **kwargs):
        if 'warehouse_id' in kwargs:
            del kwargs['warehouse_id']
        sub_period_obj = period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            rp_stock = cls.objects.filter(
                tenant=doc_obj.tenant,
                company=doc_obj.company,
                product=product_obj,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                **kwargs
            ).first()
            if not rp_stock:
                rp_stock = cls.objects.create(
                    tenant=doc_obj.tenant,
                    company=doc_obj.company,
                    product=product_obj,
                    period_mapped=period_obj,
                    sub_period_order=sub_period_order,
                    sub_period=sub_period_obj,
                    employee_created=doc_obj.employee_created if doc_obj.employee_created else doc_obj.employee_inherit,
                    employee_inherit=doc_obj.employee_inherit if doc_obj.employee_inherit else doc_obj.employee_created,
                    **kwargs
                )
            return rp_stock
        raise serializers.ValidationError({'Sub period missing': 'Sub period object does not exist.'})

    class Meta:
        verbose_name = 'Report Stock'
        verbose_name_plural = 'Report Stocks'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()


class ReportStockLog(DataAbstractModel):
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
        on_delete=models.CASCADE,
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
    ) # Kho vật lí (để hiển thị lên báo cáo trong trường hợp không quản lí tồn kho theo từng kho riêng biệt)
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="report_stock_log_sale_order",
        null=True
    )
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        related_name="report_stock_log_lease_order",
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

    perpetual_current_quantity = models.FloatField(default=0, help_text='is quantity current in perpetual')
    perpetual_current_cost = models.FloatField(default=0, help_text='is cost current in perpetual')
    perpetual_current_value = models.FloatField(default=0, help_text='is value current in perpetual')

    periodic_current_quantity = models.FloatField(default=0, help_text='is quantity current in periodic')
    periodic_current_cost = models.FloatField(default=0, help_text='is cost current in periodic')
    periodic_current_value = models.FloatField(default=0, help_text='is value current in periodic')

    lot_data = models.JSONField(default=list)

    fifo_pushed_quantity = models.IntegerField(default=0) # để biết được đã bị lấy bao nhiêu rồi
    fifo_cost_detail = models.JSONField(default=list)

    @classmethod
    def create_new_logs(cls, doc_obj, doc_data, period_obj, sub_period_order, cost_cfg):
        """ Step 1: Hàm tạo các log mới """
        bulk_info = []
        log_order_number = 0
        for item in doc_data:
            kw_parameter = {}
            if 1 in cost_cfg:
                kw_parameter['warehouse_id'] = item.get('warehouse').id if item.get('warehouse') else None
            if 2 in cost_cfg:
                kw_parameter['lot_mapped_id'] = item.get('lot_data', {}).get('lot_id') if len(
                    item.get('lot_data', {})
                ) > 0 else None
            if 3 in cost_cfg:
                kw_parameter['sale_order_id'] = item.get('sale_order').id if item.get('sale_order') else None
                kw_parameter['lease_order_id'] = item.get('lease_order').id if item.get('lease_order') else None

            rp_stock = ReportStock.get_or_create_report_stock(
                doc_obj, period_obj, sub_period_order, item['product'], **kw_parameter
            )

            latest_cost = {}
            if item['product'].valuation_method == 0:
                if item['stock_type'] == -1:
                    latest_cost = ReportInventorySubFunction.get_export_cost_for_fifo(
                        doc_obj.company.company_config.definition_inventory_valuation,
                        item['product'], item['warehouse'], item['quantity'], **kw_parameter
                    )
                    item['cost'] = latest_cost['cost']
            if item['product'].valuation_method == 1:
                if item['stock_type'] == -1:
                    latest_cost = ReportInventorySubFunction.get_latest_log_cost_dict(
                        doc_obj.company.company_config.definition_inventory_valuation,
                        item['product'], item['warehouse'], **kw_parameter
                    )
                    item['cost'] = latest_cost['cost']

            item['value'] = item['cost'] * item['quantity']

            if len(item.get('lot_data', {})) != 0:   # update Lot
                item['lot_data']['quantity'] = item['quantity']
                item['lot_data']['lot_value'] = item['value']

            if float(item['quantity']) > 0:
                log_order_number += 1
                new_log = cls(
                    tenant=doc_obj.tenant,
                    company=doc_obj.company,
                    employee_created=doc_obj.employee_created
                    if doc_obj.employee_created else doc_obj.employee_inherit,
                    employee_inherit=doc_obj.employee_inherit
                    if doc_obj.employee_inherit else doc_obj.employee_created,
                    report_stock=rp_stock,
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
                    fifo_cost_detail=latest_cost.get('fifo_cost_detail', []),
                    **kw_parameter
                )
                bulk_info.append(new_log)

                if 'sale_order_id' in kw_parameter:  # Project
                    GoodsRegistration.update_registration_inventory(item, doc_obj)
        new_logs = cls.objects.bulk_create(bulk_info)
        return new_logs

    @classmethod
    def update_log_cost_dict(cls, div, log, latest_cost):
        """ cập nhập giá cost hiện tại cho log """
        if div == 0:
            if log.product.valuation_method == 0:
                new_cost_dict = ReportInventoryValuationMethod.fifo_in_perpetual(log, latest_cost)
                log.perpetual_current_quantity = new_cost_dict['quantity'] if new_cost_dict['quantity'] > 0 else 0
                log.perpetual_current_cost = new_cost_dict['cost'] if new_cost_dict['quantity'] > 0 else 0
                log.perpetual_current_value = new_cost_dict['value'] if new_cost_dict['quantity'] > 0 else 0
                log.save(update_fields=[
                    'perpetual_current_quantity',
                    'perpetual_current_cost',
                    'perpetual_current_value'
                ])
            if log.product.valuation_method == 1:
                new_cost_dict = ReportInventoryValuationMethod.weighted_average_in_perpetual(log, latest_cost)
                log.perpetual_current_quantity = new_cost_dict['quantity'] if new_cost_dict['quantity'] > 0 else 0
                log.perpetual_current_cost = new_cost_dict['cost'] if new_cost_dict['quantity'] > 0 else 0
                log.perpetual_current_value = new_cost_dict['value'] if new_cost_dict['quantity'] > 0 else 0
                log.save(update_fields=[
                    'perpetual_current_quantity',
                    'perpetual_current_cost',
                    'perpetual_current_value'
                ])
        else:
            if log.product.valuation_method == 0:
                pass
            if log.product.valuation_method == 1:
                new_cost_dict = ReportInventoryValuationMethod.weighted_average_in_periodic(log, latest_cost)
                # chỗ này k cần check SL = 0 -> cost = 0 vì mọi TH cost đều = 0
                log.periodic_current_quantity = new_cost_dict['quantity']
                log.periodic_current_cost = 0
                log.periodic_current_value = 0
                log.save(update_fields=[
                    'periodic_current_quantity',
                    'periodic_current_cost',
                    'periodic_current_value'
                ])
        return log

    @classmethod
    def update_log_cost(cls, log, period_obj, sub_period_order, cost_cfg):
        """ Step 2: Hàm để cập nhập giá trị tồn kho khi log được ghi vào """
        kw_parameter = {}
        if 1 in cost_cfg:
            kw_parameter['warehouse_id'] = log.warehouse_id
        if 2 in cost_cfg:
            kw_parameter['lot_mapped_id'] = log.lot_mapped_id
        if 3 in cost_cfg:
            kw_parameter['sale_order_id'] = log.sale_order_id
            kw_parameter['lease_order_id'] = log.lease_order_id

        div = log.company.company_config.definition_inventory_valuation

        latest_cost = ReportInventorySubFunction.get_latest_log_cost_dict(
            div, log.product, log.physical_warehouse, **kw_parameter
        )

        updated_log = cls.update_log_cost_dict(div, log, latest_cost)

        cls.create_or_update_this_sub_period_cost(
            updated_log, period_obj, sub_period_order, latest_cost, div, **kw_parameter
        )

        return True

    @classmethod
    def for_perpetual(cls, this_sub_period_cost, log, period_obj, sub_period_order, new_cost_dict, **kwargs):
        ending_balance_quantity = new_cost_dict['quantity'] + (log.quantity * log.stock_type)
        if not this_sub_period_cost:  # không có thì tạo, gán sub_latest_log
            this_sub_period_cost = ReportInventoryCost.objects.create(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                employee_created=log.employee_created,
                employee_inherit=log.employee_inherit if log.employee_inherit else log.employee_created,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                opening_balance_quantity=new_cost_dict['quantity'],
                opening_balance_cost=new_cost_dict['cost'],
                opening_balance_value=new_cost_dict['value'],
                ending_balance_quantity=ending_balance_quantity,
                ending_balance_cost=log.perpetual_current_cost,
                ending_balance_value=ending_balance_quantity * log.perpetual_current_cost,
                sub_latest_log=log,
                **kwargs
            )
        else:  # nếu có thì update giá cost, gán sub_latest_log
            this_sub_period_cost.ending_balance_quantity = ending_balance_quantity
            this_sub_period_cost.ending_balance_cost = log.perpetual_current_cost
            this_sub_period_cost.ending_balance_value = ending_balance_quantity * log.perpetual_current_cost
            this_sub_period_cost.sub_latest_log = log

        if log.stock_type == 1:
            # nếu là nhập thì cộng tổng SL nhập và tổng Value nhập
            this_sub_period_cost.sum_input_quantity += log.quantity
            this_sub_period_cost.sum_input_value += log.quantity * log.cost
        else:
            # nếu là xuất thì cập nhập SL xuất
            this_sub_period_cost.sum_output_quantity += log.quantity
            this_sub_period_cost.sum_output_value += log.quantity * log.cost
        this_sub_period_cost.save(update_fields=[
            'sum_input_quantity',
            'sum_input_value',
            'sum_output_quantity',
            'sum_output_value',
            'ending_balance_quantity',
            'ending_balance_cost',
            'ending_balance_value',
            'sub_latest_log'
        ])
        return this_sub_period_cost

    @classmethod
    def for_periodic(cls, this_sub_period_cost, log, period_obj, sub_period_order, new_cost_dict, **kwargs):
        ending_balance_quantity = new_cost_dict['quantity'] + (log.quantity * log.stock_type)
        if not this_sub_period_cost:
            this_sub_period_cost = ReportInventoryCost.objects.create(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                employee_created=log.employee_created,
                employee_inherit=log.employee_inherit if log.employee_inherit else log.employee_created,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first(),
                opening_balance_quantity=new_cost_dict['quantity'],
                opening_balance_cost=new_cost_dict['cost'],
                opening_balance_value=new_cost_dict['value'],
                periodic_ending_balance_quantity=ending_balance_quantity,
                periodic_ending_balance_cost=log.perpetual_current_cost,
                periodic_ending_balance_value=ending_balance_quantity * log.perpetual_current_cost,
                sub_latest_log=log,
                **kwargs
            )
        else:  # có thì update giá cost, gán sub
            this_sub_period_cost.periodic_ending_balance_quantity = ending_balance_quantity
            this_sub_period_cost.periodic_ending_balance_cost = log.perpetual_current_cost
            this_sub_period_cost.periodic_ending_balance_value = ending_balance_quantity * log.perpetual_current_cost
            this_sub_period_cost.sub_latest_log = log
            # nếu kì đã đóng mà có giao dịch, mở lại, cost-value hiện tại trở về 0 (chưa chốt)
            if this_sub_period_cost.periodic_closed:
                this_sub_period_cost.periodic_closed = False
                this_sub_period_cost.periodic_ending_balance_cost = 0
                this_sub_period_cost.periodic_ending_balance_value = 0

        if log.stock_type == 1:
            # nếu là input thì cộng tổng SL nhập và tổng Value nhập
            this_sub_period_cost.sum_input_quantity += log.quantity
            this_sub_period_cost.sum_input_value += log.quantity * log.cost
        else:
            # nếu là xuất thì cập nhập SL xuất
            this_sub_period_cost.sum_output_quantity += log.quantity
            this_sub_period_cost.sum_output_quantity += log.quantity
        this_sub_period_cost.save(update_fields=[
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
        return this_sub_period_cost

    @classmethod
    def create_or_update_this_sub_period_cost(cls, log, period_obj, sub_period_order, latest_cost, div, **kwargs):
        """
        Step 3: Hàm kiểm tra record cost của sp này trong kì nay đã có hay chưa ?
                Chưa thì tạo mới - Có thì Update lại quantity-cost-value
        """
        sub_period_obj = period_obj.sub_periods_period_mapped.filter(order=sub_period_order).first()
        if sub_period_obj:
            sum_ending_quantity = 0
            for record in ReportInventoryCostLatestLog.objects.filter(product_id=log.product_id, **kwargs):
                sum_ending_quantity += record.latest_log.perpetual_current_quantity
            new_cost_dict = {
                'quantity': sum_ending_quantity,
                'cost': latest_cost['cost'],
                'value': sum_ending_quantity * latest_cost['cost']
            }
            this_sub_period_cost = ReportInventoryCost.objects.filter(
                tenant_id=log.tenant_id,
                company_id=log.company_id,
                product=log.product,
                period_mapped=period_obj,
                sub_period_order=sub_period_order,
                sub_period=sub_period_obj,
                **kwargs
            ).first()

            this_sub_period_cost = cls.for_perpetual(
                this_sub_period_cost, log, period_obj, sub_period_order, new_cost_dict, **kwargs
            ) if div == 0 else cls.for_periodic(
                this_sub_period_cost, log, period_obj, sub_period_order, new_cost_dict, **kwargs
            )

            if this_sub_period_cost:
                if 'sale_order_id' in kwargs:  # Project
                    this_sub_period_cost_wh = this_sub_period_cost.report_inventory_cost_wh.filter(
                        warehouse=log.physical_warehouse
                    ).first()
                    if this_sub_period_cost_wh:
                        this_sub_period_cost_wh.ending_quantity += log.quantity * log.stock_type
                        this_sub_period_cost_wh.save(update_fields=['ending_quantity'])
                    else:
                        last_ending_quantity = ReportInventoryCostByWarehouse.get_project_last_ending_quantity(
                            this_sub_period_cost, log.physical_warehouse
                        )
                        ReportInventoryCostByWarehouse.objects.create(
                            report_inventory_cost=this_sub_period_cost,
                            warehouse=log.physical_warehouse,
                            opening_quantity=last_ending_quantity,
                            ending_quantity=last_ending_quantity + log.quantity * log.stock_type
                        )

                # cập nhập log mới nhất, không có thì tạo mới
                if 'warehouse_id' not in kwargs:
                    kwargs['warehouse_id'] = log.physical_warehouse_id
                latest_log_obj = log.product.rp_inv_cost_product.filter(**kwargs).first()
                if latest_log_obj:
                    latest_log_obj.latest_log = log
                    latest_log_obj.save(update_fields=['latest_log'])
                else:
                    if log.product.valuation_method == 0:
                        ReportInventoryCostLatestLog.objects.create(
                            product=log.product, latest_log=log, fifo_flag_log=log, **kwargs
                        )
                    if log.product.valuation_method == 1:
                        ReportInventoryCostLatestLog.objects.create(
                            product=log.product, latest_log=log, **kwargs
                        )
            return True
        raise serializers.ValidationError({'Sub period missing': 'Sub period of this period does not exist.'})

    class Meta:
        verbose_name = 'Report Stock Log'
        verbose_name_plural = 'Report Stock Logs'
        ordering = ('-system_date',)
        default_permissions = ()
        permissions = ()


class ReportInventoryCost(DataAbstractModel):
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
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        related_name="report_inventory_cost_lease_order",
        null=True
    )

    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
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

    sum_input_quantity = models.FloatField(default=0)
    sum_input_value = models.FloatField(default=0)
    sum_output_quantity = models.FloatField(default=0)
    sum_output_value = models.FloatField(default=0)

    periodic_closed = models.BooleanField(default=False, help_text='is True if sub has closed')

    for_balance_init = models.BooleanField(default=False, help_text='is True if it has balance')
    sub_latest_log = models.ForeignKey(
        ReportStockLog,
        on_delete=models.CASCADE,
        null=True,
    ) # đây là giao dịch gần nhất trong tháng này

    class Meta:
        verbose_name = 'Report Inventory Cost'
        verbose_name_plural = 'Report Inventory Costs'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ReportInventoryCostByWarehouse(SimpleAbstractModel):
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
    def get_project_last_ending_quantity(cls, report_inventory_cost, warehouse):
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


class ReportInventoryCostLatestLog(SimpleAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='rp_inv_cost_product',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='rp_inv_cost_warehouse',
        null=True
    )
    lot_mapped = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        related_name='rp_inv_cost_lot_mapped',
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="rp_inv_cost_sale_order",
        null=True
    )
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        related_name="rp_inv_cost_lease_order",
        null=True
    )
    latest_log = models.ForeignKey(
        ReportStockLog,
        on_delete=models.CASCADE,
        null=True,
        related_name='rp_inv_cost_latest_log'
    ) # lấy giá cost hiện tại dựa vào latest_log này

    fifo_flag_log = models.ForeignKey(
        ReportStockLog,
        on_delete=models.CASCADE,
        null=True,
        related_name='rp_inv_cost_fifo_flag_log'
    ) # để biết được bắt đầu lấy cost từ đâu (cho SP FIFO)

    class Meta:
        verbose_name = 'Latest Log'
        verbose_name_plural = 'Latest Log'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ReportInventorySubFunction:
    @classmethod
    def get_latest_month_log(cls, period_obj, sub_period_order, product_id, **kwargs):
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
    def get_latest_log_cost_dict(cls, div, product, physical_warehouse, **kwargs):
        """ lấy cost dict của log gần nhất """
        record = ReportInventoryCostLatestLog.objects.filter(
            product=product, warehouse=physical_warehouse, **kwargs
        ).first() if 'warehouse_id' not in kwargs else ReportInventoryCostLatestLog.objects.filter(
            product=product, **kwargs
        ).first()
        latest_log = record.latest_log if record else None
        if latest_log:
            return {
                'quantity': latest_log.perpetual_current_quantity,
                'cost': latest_log.perpetual_current_cost,
                'value': latest_log.perpetual_current_value
            } if div == 0 else {
                'quantity': latest_log.periodic_current_quantity,
                'cost': 0,
                'value': 0
            }
        return cls.get_opening_cost_dict(product.id, 3, **kwargs)

    @classmethod
    def get_export_cost_for_fifo(cls, div, product, physical_warehouse, quantity, **kwargs):
        record = ReportInventoryCostLatestLog.objects.filter(
            product=product, warehouse=physical_warehouse, **kwargs
        ).first() if 'warehouse_id' not in kwargs else ReportInventoryCostLatestLog.objects.filter(
            product=product, **kwargs
        ).first()
        fifo_flag_log = record.fifo_flag_log if record else None
        latest_log = record.latest_log if record else None
        if fifo_flag_log and latest_log:
            pushed_quantity = quantity
            fifo_cost_detail = []
            for stock_log in ReportStockLog.objects.filter(
                    product=product, stock_type=1, system_date__gte=fifo_flag_log.system_date, **kwargs
            ).order_by('system_date'):
                if stock_log.quantity - stock_log.fifo_pushed_quantity < pushed_quantity:
                    fifo_cost_detail.append({
                        'log_trans_id': str(stock_log.id),
                        'log_trans_code': stock_log.trans_code,
                        'log_fifo_pushed_quantity': stock_log.quantity - stock_log.fifo_pushed_quantity,
                        'log_value': stock_log.cost * (stock_log.quantity - stock_log.fifo_pushed_quantity)
                    })
                    pushed_quantity -= stock_log.quantity - stock_log.fifo_pushed_quantity
                    stock_log.fifo_pushed_quantity += stock_log.quantity - stock_log.fifo_pushed_quantity
                    stock_log.save(update_fields=['fifo_pushed_quantity'])
                else:
                    fifo_cost_detail.append({
                        'log_trans_id': str(stock_log.id),
                        'log_trans_code': stock_log.trans_code,
                        'log_fifo_pushed_quantity': pushed_quantity,
                        'log_value': stock_log.cost * pushed_quantity
                    })
                    stock_log.fifo_pushed_quantity += pushed_quantity
                    stock_log.save(update_fields=['fifo_pushed_quantity'])
                    record = ReportInventoryCostLatestLog.objects.filter(product=product, **kwargs).first()
                    if record:
                        record.fifo_flag_log = stock_log
                        record.save(update_fields=['fifo_flag_log'])
                    break

            export_fifo_cost = (sum(item['log_value'] for item in fifo_cost_detail) / quantity) if quantity > 0 else 0
            return {'cost': export_fifo_cost, 'fifo_cost_detail': fifo_cost_detail} if div == 0 else 0
        return {
            'cost': cls.get_opening_cost_dict(product.id, 3, **kwargs)['cost'],
            'fifo_cost_detail': []
        }

    @classmethod
    def get_opening_cost_dict(cls, product_id, data_type=1, **kwargs):
        """ Hàm tìm số dư đầu kì """
        this_record = ReportInventoryCost.objects.filter(product_id=product_id, for_balance_init=True, **kwargs).first()
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
    def get_this_sub_period_cost_dict(cls, this_sub_period_cost, warehouse_id=None):
        """ Hàm lấy opening và ending của kỳ này """
        if not warehouse_id:
            # Get Opening
            opening_quantity = this_sub_period_cost.opening_balance_quantity
            opening_cost = this_sub_period_cost.opening_balance_cost
            opening_value = this_sub_period_cost.opening_balance_value

            # Get Ending
            ending_quantity, ending_cost, ending_value = (
                this_sub_period_cost.ending_balance_quantity,
                this_sub_period_cost.ending_balance_cost,
                this_sub_period_cost.ending_balance_value
            ) if this_sub_period_cost.company.company_config.definition_inventory_valuation == 0 else (
                this_sub_period_cost.periodic_ending_balance_quantity,
                this_sub_period_cost.periodic_ending_balance_cost,
                this_sub_period_cost.periodic_ending_balance_value
            )
        else:
            this_sub_period_cost_wh = this_sub_period_cost.report_inventory_cost_wh.filter(
                warehouse_id=warehouse_id
            ).first()
            if this_sub_period_cost_wh:
                # Get Opening
                opening_quantity = this_sub_period_cost_wh.opening_quantity
                opening_cost = this_sub_period_cost.opening_balance_cost
                opening_value = opening_quantity * opening_cost

                # Get Ending
                ending_quantity, ending_cost, ending_value = (
                    this_sub_period_cost_wh.ending_quantity,
                    this_sub_period_cost.ending_balance_cost,
                    this_sub_period_cost_wh.ending_quantity * this_sub_period_cost.ending_balance_cost
                ) if this_sub_period_cost.company.company_config.definition_inventory_valuation == 0 else (
                    this_sub_period_cost.periodic_ending_balance_quantity,
                    this_sub_period_cost.periodic_ending_balance_cost,
                    this_sub_period_cost.periodic_ending_balance_value
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
    def calculate_cost_dict_for_periodic(cls, period_obj, sub_period_order, tenant, company):
        """ Cập nhập giá cost cuối kì cho tháng trước """
        for this_sub_period_cost in ReportInventoryCost.objects.filter(
            tenant=tenant, company=company, period_mapped=period_obj, sub_period_order=sub_period_order
        ):
            sum_input_quantity = this_sub_period_cost.sum_input_quantity
            sum_input_value = this_sub_period_cost.sum_input_value
            sum_output_quantity = this_sub_period_cost.sum_output_quantity

            if sum_input_quantity > 0:
                quantity = sum_input_quantity - sum_output_quantity
                cost = (sum_input_value / sum_input_quantity) if sum_input_quantity > 0 else 0
                value = quantity * cost
            else:
                quantity = this_sub_period_cost.opening_balance_quantity
                cost = this_sub_period_cost.opening_balance_cost
                value = this_sub_period_cost.opening_balance_value

            this_sub_period_cost.periodic_ending_balance_quantity = quantity if quantity > 0 else 0
            this_sub_period_cost.periodic_ending_balance_cost = cost if quantity > 0 else 0
            this_sub_period_cost.periodic_ending_balance_value = value if quantity > 0 else 0
            this_sub_period_cost.periodic_closed = True
            this_sub_period_cost.save(
                update_fields=[
                    'periodic_ending_balance_quantity',
                    'periodic_ending_balance_cost',
                    'periodic_ending_balance_value',
                    'periodic_closed'
                ]
            )
        return True


class ReportInventoryValuationMethod:
    @classmethod
    def weighted_average_in_perpetual(cls, log, latest_cost):
        if log.stock_type == 1:
            new_quantity = latest_cost['quantity'] + log.quantity
            sum_value = latest_cost['value'] + log.value
            new_cost = (sum_value / new_quantity) if new_quantity > 0 else 0
            new_value = sum_value
        else:
            new_quantity = latest_cost['quantity'] - log.quantity
            new_cost = latest_cost['cost']
            new_value = new_cost * new_quantity
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def weighted_average_in_periodic(cls, log, latest_cost):
        # Lúc này sum nhập đã được cập nhập
        return {
            'quantity': latest_cost['quantity'] + (log.quantity * log.stock_type),
            'cost': 0,
            'value': 0
        }

    @classmethod
    def fifo_in_perpetual(cls, log, latest_cost):
        if log.stock_type == 1:
            new_quantity = latest_cost['quantity'] + log.quantity
            sum_value = latest_cost['value'] + log.value
            new_cost = (sum_value / new_quantity) if new_quantity > 0 else 0
            new_value = sum_value
        else:
            new_quantity = latest_cost['quantity'] - log.quantity
            new_value = latest_cost['value'] - log.value
            new_cost = (new_value / new_quantity) if new_quantity else 0
        return {'quantity': new_quantity, 'cost': new_cost, 'value': new_value}

    @classmethod
    def fifo_in_periodic(cls, log, latest_cost):
        # Lúc này sum nhập đã được cập nhập
        return {
            'quantity': latest_cost['quantity'] + (log.quantity * log.stock_type),
            'cost': 0,
            'value': 0
        }
