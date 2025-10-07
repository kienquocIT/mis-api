from django.db import models
from apps.accounting.journalentry.utils import JEForGoodsReceiptHandler
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.masterdata.saledata.models import SubPeriods, ProductWareHouseLot
from apps.sales.inventory.models.goods_detail import GoodsDetail
from apps.sales.inventory.utils import GRFinishHandler, GRHandler
from apps.sales.report.utils.log_for_goods_receipt import IRForGoodsReceiptHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel, GOODS_RECEIPT_TYPE, PRODUCTION_REPORT_TYPE


class GoodsReceipt(DataAbstractModel):
    goods_receipt_type = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(GOODS_RECEIPT_TYPE),
    )
    # FIELDS OF TYPE 0(For purchase order)
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="goods_receipt_po",
        null=True,
    )
    purchase_order_data = models.JSONField(
        default=dict,
        help_text="read data purchase_order, use for get list or detail"
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="supplier",
        related_name="goods_receipt_supplier",
        null=True,
        help_text="sale data Accounts have type supplier"
    )
    supplier_data = models.JSONField(
        default=dict,
        help_text="read data supplier, use for get list or detail"
    )
    purchase_requests = models.ManyToManyField(
        'purchasing.PurchaseRequest',
        through="GoodsReceiptPurchaseRequest",
        symmetrical=False,
        blank=True,
        related_name='goods_receipt_map_pr'
    )
    purchase_requests_data = models.JSONField(
        default=list, help_text='data json of purchase request, records in GoodsReceiptPurchaseRequest'
    )
    # FIELDS OF TYPE 1(For inventory adjustment)
    inventory_adjustment = models.ForeignKey(
        'inventory.InventoryAdjustment',
        on_delete=models.CASCADE,
        verbose_name="inventory adjustment",
        related_name="goods_receipt_ia",
        null=True,
    )
    inventory_adjustment_data = models.JSONField(
        default=dict,
        help_text="read data inventory_adjustment, use for get list or detail"
    )
    # FIELDS OF TYPE 2(For production)
    production_report_type = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(PRODUCTION_REPORT_TYPE),
    )
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        verbose_name="production order",
        related_name="goods_receipt_production_order",
        null=True,
    )
    production_order_data = models.JSONField(
        default=dict,
        help_text="read data production_order, use for get list or detail"
    )
    work_order = models.ForeignKey(
        'production.WorkOrder',
        on_delete=models.CASCADE,
        verbose_name="work order",
        related_name="goods_receipt_work_order",
        null=True,
    )
    work_order_data = models.JSONField(
        default=dict,
        help_text="read data work_order, use for get list or detail"
    )
    production_reports = models.ManyToManyField(
        'production.ProductionReport',
        through="GoodsReceiptProductionReport",
        symmetrical=False,
        blank=True,
        related_name='goods_receipt_map_production_report'
    )
    production_reports_data = models.JSONField(
        default=list, help_text='data json of production report, records in GoodsReceiptProductionReport'
    )
    product_modification = models.ForeignKey(
        'productmodification.ProductModification',
        on_delete=models.CASCADE,
        verbose_name="product modification",
        related_name="goods_receipt_product_modification",
        null=True,
    )
    product_modification_data = models.JSONField(
        default=dict,
        help_text="read data product_modification, use for get list or detail"
    )
    # COMMON FIELDS
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description of this records',
    )
    date_received = models.DateTimeField(null=True)
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='GoodsReceiptAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_goods_receipt',
    )
    gr_products_data = models.JSONField(
        default=list, help_text='data JSON of gr products, records in GoodsReceiptProduct'
    )
    # total
    total_pretax = models.FloatField(default=0)
    total_tax = models.FloatField(default=0)
    total = models.FloatField(default=0)
    total_revenue_before_tax = models.FloatField(default=0)
    # is no warehouse
    is_no_warehouse = models.BooleanField(default=False, help_text="flag to know goods receipts to warehouse or not")
    has_ap_invoice_already = models.BooleanField(
        default=False,
        help_text='is true if this Goods receipt has AP invoice'
    )

    class Meta:
        verbose_name = 'Goods Receipt'
        verbose_name_plural = 'Goods Receipts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @staticmethod
    def count_created_serial_data(good_receipt_obj, gr_prd_obj, gr_wh_obj, pr_data):
        count = 0
        for serial in good_receipt_obj.goods_receipt_serial_goods_receipt.filter(
                goods_receipt_warehouse__goods_receipt_product__product=gr_prd_obj.product,
                goods_receipt_warehouse__warehouse=gr_wh_obj.warehouse,
        ):
            if serial.goods_receipt_warehouse:
                if serial.goods_receipt_warehouse.goods_receipt_request_product:
                    sn_pr_prd = serial.goods_receipt_warehouse.goods_receipt_request_product.purchase_request_product
                    if sn_pr_prd:
                        if str(sn_pr_prd.purchase_request_id) == pr_data.get('id'):
                            count += 1
                if not serial.goods_receipt_warehouse.goods_receipt_request_product:
                    count += 1
            else:
                count += 1
        return count

    @classmethod
    def push_goods_receipt_data_to_goods_detail(cls, goods_receipt_obj):
        print(f'* Push goods receipt data ({goods_receipt_obj.code}) to goods detail.')
        bulk_info = []
        for gr_prd_obj in goods_receipt_obj.goods_receipt_product_goods_receipt.all():
            for gr_wh_obj in gr_prd_obj.goods_receipt_warehouse_gr_product.all():
                pr_data = gr_wh_obj.goods_receipt_request_product.purchase_request_data if (
                    gr_wh_obj.goods_receipt_request_product) else {}
                gr_wh_lot_list = gr_wh_obj.goods_receipt_lot_gr_warehouse.all()
                count_serial_data = cls.count_created_serial_data(
                    goods_receipt_obj, gr_prd_obj, gr_wh_obj, pr_data
                )
                if gr_wh_lot_list.count() > 0:
                    for gr_wh_lot_obj in gr_wh_lot_list:
                        bulk_info.append(GoodsDetail(
                            product=gr_prd_obj.product,
                            product_data={
                                'id': str(gr_prd_obj.product_id),
                                'code': gr_prd_obj.product.code,
                                'title': gr_prd_obj.product.title,
                                'description': gr_prd_obj.product.description,
                                'category': str(gr_prd_obj.product.general_product_category_id),
                                'general_traceability_method': gr_prd_obj.product.general_traceability_method
                            } if gr_prd_obj.product else {},
                            warehouse=gr_wh_obj.warehouse,
                            warehouse_data={
                                'id': str(gr_wh_obj.warehouse_id),
                                'code': gr_wh_obj.warehouse.code,
                                'title': gr_wh_obj.warehouse.title
                            } if gr_wh_obj.warehouse else {},
                            uom=gr_prd_obj.uom,
                            uom_data=gr_prd_obj.uom_data,
                            goods_receipt=goods_receipt_obj,
                            goods_receipt_data={
                                'id': str(goods_receipt_obj.id),
                                'code': goods_receipt_obj.code,
                                'title': goods_receipt_obj.title,
                                'date_approved': str(goods_receipt_obj.date_approved),
                                'pic': {
                                    'id': str(goods_receipt_obj.employee_inherit_id),
                                    'code': goods_receipt_obj.employee_inherit.code,
                                    'fullname': goods_receipt_obj.employee_inherit.get_full_name(2),
                                    'group': {
                                        'id': str(goods_receipt_obj.employee_inherit.group_id),
                                        'code': goods_receipt_obj.employee_inherit.group.code,
                                        'title': goods_receipt_obj.employee_inherit.group.title,
                                    } if goods_receipt_obj.employee_inherit.group else {},
                                } if goods_receipt_obj.employee_inherit else {},
                            } if goods_receipt_obj else {},
                            purchase_request_id=pr_data.get('id'),
                            purchase_request_data=pr_data,
                            lot=gr_wh_lot_obj.lot,
                            lot_data={
                                'id': str(gr_wh_lot_obj.lot_id),
                                'lot_number': gr_wh_lot_obj.lot.lot_number,
                                'expire_date': str(gr_wh_lot_obj.lot.expire_date),
                                'manufacture_date': str(gr_wh_lot_obj.lot.manufacture_date)
                            } if gr_wh_lot_obj.lot else {},
                            imported_sn_quantity=count_serial_data,
                            receipt_quantity=gr_wh_obj.quantity_import,
                            status=int(count_serial_data == gr_wh_obj.quantity_import),
                            tenant=goods_receipt_obj.tenant,
                            company=goods_receipt_obj.company,
                            employee_inherit=goods_receipt_obj.employee_inherit,
                            employee_created=goods_receipt_obj.employee_created,
                            date_created=goods_receipt_obj.date_approved
                        ))
                else:
                    bulk_info.append(GoodsDetail(
                        product=gr_prd_obj.product,
                        product_data={
                            'id': str(gr_prd_obj.product_id),
                            'code': gr_prd_obj.product.code,
                            'title': gr_prd_obj.product.title,
                            'description': gr_prd_obj.product.description,
                            'category': str(gr_prd_obj.product.general_product_category_id),
                            'general_traceability_method': gr_prd_obj.product.general_traceability_method
                        } if gr_prd_obj.product else {},
                        warehouse=gr_wh_obj.warehouse,
                        warehouse_data={
                            'id': str(gr_wh_obj.warehouse_id),
                            'code': gr_wh_obj.warehouse.code,
                            'title': gr_wh_obj.warehouse.title
                        } if gr_wh_obj.warehouse else {},
                        uom=gr_prd_obj.uom,
                        uom_data=gr_prd_obj.uom_data,
                        goods_receipt=goods_receipt_obj,
                        goods_receipt_data={
                            'id': str(goods_receipt_obj.id),
                            'code': goods_receipt_obj.code,
                            'title': goods_receipt_obj.title,
                            'date_approved': str(goods_receipt_obj.date_approved),
                            'pic': {
                                'id': str(goods_receipt_obj.employee_inherit_id),
                                'code': goods_receipt_obj.employee_inherit.code,
                                'fullname': goods_receipt_obj.employee_inherit.get_full_name(2),
                                'group': {
                                    'id': str(goods_receipt_obj.employee_inherit.group_id),
                                    'code': goods_receipt_obj.employee_inherit.group.code,
                                    'title': goods_receipt_obj.employee_inherit.group.title,
                                } if goods_receipt_obj.employee_inherit.group else {},
                            } if goods_receipt_obj.employee_inherit else {},
                        } if goods_receipt_obj else {},
                        purchase_request_id=pr_data.get('id'),
                        purchase_request_data=pr_data,
                        lot=None,
                        lot_data={},
                        imported_sn_quantity=count_serial_data,
                        receipt_quantity=gr_wh_obj.quantity_import,
                        status=int(count_serial_data == gr_wh_obj.quantity_import),
                        tenant=goods_receipt_obj.tenant,
                        company=goods_receipt_obj.company,
                        employee_inherit=goods_receipt_obj.employee_inherit,
                        employee_created=goods_receipt_obj.employee_created,
                        date_created=goods_receipt_obj.date_approved
                    ))
        GoodsDetail.objects.bulk_create(bulk_info)
        print('Done')
        return True

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_check_period', False):
            SubPeriods.check_period(self.tenant_id, self.company_id)

        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('goodsreceipt', True, self, kwargs)
                    GRFinishHandler.push_to_warehouse_stock(instance=self)
                    GRFinishHandler.push_product_info(instance=self)
                    GRFinishHandler.push_relate_gr_info(instance=self)
                    # update lot_id in GoodsReceiptLot (for new LOT)
                    for item in self.goods_receipt_lot_goods_receipt.all():
                        lot_obj = ProductWareHouseLot.objects.filter(
                            lot_number=item.lot_number,
                            product_warehouse__product=item.goods_receipt_warehouse.goods_receipt_product.product
                        ).first()
                        item.lot = lot_obj
                        item.save(update_fields=['lot'])

                    self.push_goods_receipt_data_to_goods_detail(self)
                    IRForGoodsReceiptHandler.push_to_inventory_report(self)
                    JEForGoodsReceiptHandler.push_to_journal_entry(self)

        if self.system_status in [4]:  # cancel
            GRFinishHandler.push_product_info(instance=self)

        # diagram
        GRHandler.push_diagram(instance=self)
        # hit DB
        super().save(*args, **kwargs)


class GoodsReceiptPurchaseRequest(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_pr_goods_receipt",
    )
    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE,
        verbose_name="purchase request",
        related_name="goods_receipt_pr_pr",
    )

    class Meta:
        verbose_name = 'Goods Receipt Purchase Request'
        verbose_name_plural = 'Goods Receipt Purchase Requests'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsReceiptProductionReport(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_production_report_receipt",
    )
    production_report = models.ForeignKey(
        'production.ProductionReport',
        on_delete=models.CASCADE,
        verbose_name="production report",
        related_name="goods_receipt_production_report_report",
    )

    class Meta:
        verbose_name = 'Goods Receipt Production Report'
        verbose_name_plural = 'Goods Receipt Production Reports'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsReceiptProduct(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_product_goods_receipt",
    )
    purchase_order_product = models.ForeignKey(
        'purchasing.PurchaseOrderProduct',
        on_delete=models.CASCADE,
        verbose_name="po product",
        related_name="goods_receipt_product_po_product",
        null=True
    )
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        verbose_name="production order",
        related_name="goods_receipt_product_production_order",
        null=True
    )
    work_order = models.ForeignKey(
        'production.WorkOrder',
        on_delete=models.CASCADE,
        verbose_name="work order",
        related_name="goods_receipt_product_work_order",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="goods_receipt_product_product",
        null=True
    )
    product_modification_product = models.ForeignKey(
        'productmodification.RemovedComponent',
        on_delete=models.SET_NULL,
        verbose_name="pm product",
        related_name="goods_receipt_product_pm_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data JSON of product')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit of measure",
        related_name="goods_receipt_product_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data JSON of uom')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="goods_receipt_product_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data JSON of tax')
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="goods_receipt_product_warehouse",
        null=True
    )
    warehouse_data = models.JSONField(default=dict, help_text='data JSON of warehouse')
    product_quantity_order_actual = models.FloatField(default=0, help_text='quantity order')
    quantity_import = models.FloatField(default=0, help_text='quantity goods receipt this time')
    product_title = models.TextField(blank=True)
    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_description = models.TextField(
        blank=True,
        null=True
    )
    product_unit_price = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    is_additional = models.BooleanField(
        default=False, help_text='flag to know enter quantity first, add lot/serial later'
    )
    ia_item = models.ForeignKey(
        'inventory.InventoryAdjustmentItem',
        on_delete=models.SET_NULL,
        null=True,
        related_name='goods_receipt_product_ia_item'
    )
    is_added = models.BooleanField(
        default=False, help_text='flag to know that lot/serial is all added by Goods Detail'
    )
    pr_products_data = models.JSONField(
        default=list, help_text='data JSON of pr products, records in GoodsReceiptRequestProduct'
    )
    gr_warehouse_data = models.JSONField(
        default=list, help_text='data JSON of gr warehouse, records in GoodsReceiptWarehouse'
    )

    class Meta:
        verbose_name = 'Goods Receipt Product'
        verbose_name_plural = 'Goods Receipt Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class GoodsReceiptRequestProduct(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_request_product_goods_receipt",
    )
    goods_receipt_product = models.ForeignKey(
        GoodsReceiptProduct,
        on_delete=models.CASCADE,
        verbose_name="goods receipt product",
        related_name="goods_receipt_request_product_gr_product",
        null=True
    )
    purchase_order_request_product = models.ForeignKey(
        'purchasing.PurchaseOrderRequestProduct',
        on_delete=models.CASCADE,
        verbose_name="purchase order request product",
        related_name="gr_request_product_po_request_product",
        null=True
    )
    purchase_request_product = models.ForeignKey(
        'purchasing.PurchaseRequestProduct',
        on_delete=models.CASCADE,
        verbose_name="purchase request product",
        related_name="goods_receipt_request_product_pr_product",
        null=True
    )
    purchase_request_data = models.JSONField(default=dict, help_text='data JSON of purchase request')
    production_report = models.ForeignKey(
        'production.ProductionReport',
        on_delete=models.CASCADE,
        verbose_name="production report",
        related_name="gr_request_product_production_report",
        null=True
    )
    production_report_data = models.JSONField(default=dict, help_text='data JSON of production report')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit of measure",
        related_name="gr_request_product_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data JSON of uom')
    quantity_order = models.FloatField(default=0, help_text='quantity purchase order')
    quantity_import = models.FloatField(default=0, help_text='quantity goods receipt')
    is_stock = models.BooleanField(
        default=False,
        help_text="True if GR direct to stock, stock is created from PO when quantity order > quantity request"
    )
    gr_warehouse_data = models.JSONField(
        default=list, help_text='data JSON of gr warehouse, records in GoodsReceiptWarehouse'
    )

    class Meta:
        verbose_name = 'Goods Receipt Request Product'
        verbose_name_plural = 'Goods Receipt Request Products'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsReceiptWarehouse(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_warehouse_goods_receipt",
    )
    goods_receipt_request_product = models.ForeignKey(
        GoodsReceiptRequestProduct,
        on_delete=models.CASCADE,
        verbose_name="goods receipt request product",
        related_name="goods_receipt_warehouse_request_product",
        null=True
    )
    goods_receipt_product = models.ForeignKey(
        GoodsReceiptProduct,
        on_delete=models.CASCADE,
        verbose_name="goods receipt product",
        related_name="goods_receipt_warehouse_gr_product",
        null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="goods_receipt_warehouse_warehouse",
        null=True
    )
    warehouse_data = models.JSONField(default=dict, help_text='data JSON of warehouse')
    uom_data = models.JSONField(default=dict, help_text='data JSON of uom')
    quantity_import = models.FloatField(default=0)
    is_additional = models.BooleanField(
        default=False, help_text='flag to know enter quantity first, add lot/serial later'
    )
    is_added = models.BooleanField(
        default=False, help_text='flag to know that lot/serial is all added by Goods Detail'
    )
    lot_data = models.JSONField(default=list, help_text='data JSON of lots, records in GoodsReceiptLot')
    serial_data = models.JSONField(default=list, help_text='data JSON of serials, records in GoodsReceiptSerial')

    class Meta:
        verbose_name = 'Goods Receipt Warehouse'
        verbose_name_plural = 'Goods Receipt Warehouses'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsReceiptLot(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_lot_goods_receipt",
    )
    goods_receipt_warehouse = models.ForeignKey(
        GoodsReceiptWarehouse,
        on_delete=models.CASCADE,
        verbose_name="goods receipt warehouse",
        related_name="goods_receipt_lot_gr_warehouse",
    )
    lot = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        verbose_name="product warehouse lot",
        related_name="goods_receipt_lot_lot",
        null=True,
    )
    lot_number = models.CharField(max_length=100, blank=True, null=True)
    quantity_import = models.FloatField(default=0)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Goods Receipt Lot'
        verbose_name_plural = 'Goods Receipt Lots'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsReceiptSerial(SimpleAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_serial_goods_receipt",
    )
    goods_receipt_warehouse = models.ForeignKey(
        GoodsReceiptWarehouse,
        on_delete=models.CASCADE,
        verbose_name="goods receipt warehouse",
        related_name="goods_receipt_serial_gr_warehouse",
    )
    vendor_serial_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    expire_date = models.DateTimeField(null=True)
    manufacture_date = models.DateTimeField(null=True)
    warranty_start = models.DateTimeField(null=True)
    warranty_end = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Goods Receipt Serial'
        verbose_name_plural = 'Goods Receipt Serials'
        ordering = ()
        default_permissions = ()
        permissions = ()


class GoodsReceiptAttachment(M2MFilesAbstractModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        verbose_name="goods receipt",
        related_name="goods_receipt_attachment_gr",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'goods_receipt'

    class Meta:
        verbose_name = 'Goods receipt attachments'
        verbose_name_plural = 'Goods receipt attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
