from django.db import models
from apps.masterdata.saledata.models import SubPeriods, ProductWareHouseLot
from apps.sales.inventory.models.goods_registration import GoodsRegistration
from apps.sales.inventory.utils import GRFinishHandler, GRHandler
from apps.sales.report.models import ReportInventorySub
from apps.shared import DataAbstractModel, SimpleAbstractModel, GOODS_RECEIPT_TYPE


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
    # COMMON FIELDS
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description of this records',
    )
    date_received = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Goods Receipt'
        verbose_name_plural = 'Goods Receipts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("GR")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'GR0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'GR{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def get_all_lots(cls, instance):
        all_lots_in_gr = list({lot.lot_number for lot in instance.goods_receipt_lot_goods_receipt.all()})
        all_lots = ProductWareHouseLot.objects.filter(lot_number__in=all_lots_in_gr)
        return all_lots

    @classmethod
    def for_goods_receipt_has_no_purchase_request(cls, instance, stock_data, all_lots):
        goods_receipt_warehouses = instance.goods_receipt_warehouse_goods_receipt.all()
        for gr_item in instance.goods_receipt_product_goods_receipt.all():
            if gr_item.product.general_traceability_method != 1:  # None + Sn
                for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
                    casted_quantity = ReportInventorySub.cast_quantity_to_unit(
                        gr_item.uom, gr_prd_wh.quantity_import
                    )
                    casted_cost = (
                        gr_item.product_unit_price * gr_prd_wh.quantity_import / casted_quantity
                    ) if casted_quantity > 0 else 0
                    stock_data.append({
                        'product': gr_item.product,
                        'warehouse': gr_prd_wh.warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': 1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods receipt (IA)' if instance.goods_receipt_type else 'Goods receipt',
                        'quantity': casted_quantity,
                        'cost': casted_cost,
                        'value': casted_cost * casted_quantity,
                        'lot_data': {}
                    })
            else:  # lot
                for gr_prd_wh in goods_receipt_warehouses.filter(goods_receipt_product__product=gr_item.product):
                    for lot in gr_prd_wh.goods_receipt_lot_gr_warehouse.all():
                        casted_quantity = ReportInventorySub.cast_quantity_to_unit(gr_item.uom, lot.quantity_import)
                        casted_cost = (
                            gr_item.product_unit_price * lot.quantity_import / casted_quantity
                        ) if casted_quantity > 0 else 0
                        stock_data.append({
                            'product': gr_item.product,
                            'warehouse': gr_prd_wh.warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': 1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods receipt (IA)' if instance.goods_receipt_type else 'Goods receipt',
                            'quantity': casted_quantity,
                            'cost': casted_cost,
                            'value': casted_cost * casted_quantity,
                            'lot_data': {
                                'lot_id': str(all_lots.filter(lot_number=lot.lot_number).first().id),
                                'lot_number': lot.lot_number,
                                'lot_quantity': casted_quantity,
                                'lot_value': casted_quantity * gr_item.product_unit_price,
                                'lot_expire_date': str(lot.expire_date) if lot.expire_date else None
                            }
                        })
        return stock_data

    @classmethod
    def for_goods_receipt_has_purchase_request(cls, instance, stock_data, all_lots):
        for gr_item in instance.goods_receipt_product_goods_receipt.all():
            for pr_product in gr_item.goods_receipt_request_product_gr_product.all():
                purchase_request = None
                if pr_product.purchase_request_product:
                    purchase_request = pr_product.purchase_request_product.purchase_request
                for prd_wh in pr_product.goods_receipt_warehouse_request_product.all():
                    if gr_item.product.general_traceability_method != 1:
                        casted_quantity = ReportInventorySub.cast_quantity_to_unit(
                            gr_item.uom, prd_wh.quantity_import
                        )
                        casted_cost = (
                            gr_item.product_unit_price * prd_wh.quantity_import / casted_quantity
                        ) if casted_quantity > 0 else 0
                        stock_data.append({
                            'sale_order': purchase_request.sale_order if purchase_request else None,
                            'product': gr_item.product,
                            'warehouse': prd_wh.warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': 1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods receipt (IA)' if instance.goods_receipt_type else 'Goods receipt',
                            'quantity': casted_quantity,
                            'cost': casted_cost,
                            'value': casted_cost * casted_quantity,
                            'lot_data': {}
                        })
                    else:
                        for lot in prd_wh.goods_receipt_lot_gr_warehouse.all():
                            casted_quantity = ReportInventorySub.cast_quantity_to_unit(
                                gr_item.uom, lot.quantity_import
                            )
                            casted_cost = (
                                gr_item.product_unit_price * lot.quantity_import / casted_quantity
                            ) if casted_quantity > 0 else 0
                            stock_data.append({
                                'sale_order': purchase_request.sale_order if purchase_request else None,
                                'product': gr_item.product,
                                'warehouse': prd_wh.warehouse,
                                'system_date': instance.date_approved,
                                'posting_date': instance.date_approved,
                                'document_date': instance.date_approved,
                                'stock_type': 1,
                                'trans_id': str(instance.id),
                                'trans_code': instance.code,
                                'trans_title': 'Goods receipt (IA)'
                                if instance.goods_receipt_type else 'Goods receipt',
                                'quantity': casted_quantity,
                                'cost': casted_cost,
                                'value': casted_cost * casted_quantity,
                                'lot_data': {
                                    'lot_id': str(all_lots.filter(lot_number=lot.lot_number).first().id),
                                    'lot_number': lot.lot_number,
                                    'lot_quantity': casted_quantity,
                                    'lot_value': casted_quantity * gr_item.product_unit_price,
                                    'lot_expire_date': str(lot.expire_date) if lot.expire_date else None
                                }
                            })
        return stock_data

    @classmethod
    def prepare_data_for_logging(cls, instance):
        all_lots = cls.get_all_lots(instance)
        stock_data = []
        if instance.goods_receipt_pr_goods_receipt.count() == 0:
            stock_data = cls.for_goods_receipt_has_no_purchase_request(instance, stock_data, all_lots)
        else:
            stock_data = cls.for_goods_receipt_has_purchase_request(instance, stock_data, all_lots)
        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_approved,
            stock_data
        )
        return stock_data

    @classmethod
    def regis_stock_when_receipt(cls, instance, stock_data):
        if instance.company.company_config.cost_per_project:  # Case 5
            for po_pr_mapped in instance.purchase_order.purchase_order_request_order.all():
                sale_order = po_pr_mapped.purchase_request.sale_order
                if sale_order:
                    for item in stock_data:
                        GoodsRegistration.update_registered_quantity_when_receipt(sale_order, item)
            return True

    def save(self, *args, **kwargs):
        SubPeriods.check_open(
            self.company_id,
            self.tenant_id,
            self.date_approved if self.date_approved else self.date_created
        )

        if self.system_status in [2, 3]:  # added, finish
            # check if not code then generate code
            if not self.code:
                self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                # if self.inventory_adjustment:
                #     self.inventory_adjustment.update_ia_state()

            # check if date_approved then call related functions
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    if 'date_approved' in kwargs['update_fields']:
                        GRFinishHandler.push_to_warehouse_stock(self)
                        GRFinishHandler.push_product_info(self)
                        GRFinishHandler.update_gr_info_for_po(self)
                        GRFinishHandler.update_gr_info_for_ia(self)
                        GRFinishHandler.update_is_all_receipted_po(self)
                        GRFinishHandler.update_is_all_receipted_ia(self)

            stock_data = self.prepare_data_for_logging(self)
            self.regis_stock_when_receipt(self, stock_data)

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
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="goods_receipt_product_product",
        null=True
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit of measure",
        related_name="goods_receipt_product_uom",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="goods_receipt_product_tax",
        null=True
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="warehouse",
        related_name="goods_receipt_product_warehouse",
        null=True
    )
    quantity_import = models.FloatField(default=0)
    product_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
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
    quantity_import = models.FloatField(default=0)
    is_stock = models.BooleanField(
        default=False,
        help_text="True if GR direct to stock, stock is created from PO when quantity order > quantity request"
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
    quantity_import = models.FloatField(default=0)
    is_additional = models.BooleanField(
        default=False, help_text='flag to know enter quantity first, add lot/serial later'
    )
    is_added = models.BooleanField(
        default=False, help_text='flag to know that lot/serial is all added by Goods Detail'
    )

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
