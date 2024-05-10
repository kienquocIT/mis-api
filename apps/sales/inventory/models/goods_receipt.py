from django.db import models
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.inventory.utils import GRFinishHandler
from apps.sales.inventory.utils.logical_gr import GRHandler
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
    def check_exist(cls, item_product_id, item_warehouse_id, item_trans_id, activities_data):
        for obj in activities_data:
            if all([
                item_product_id == obj['product'].id,
                item_warehouse_id == obj['warehouse'].id,
                item_trans_id == obj['trans_id']
            ]):
                return obj
        return None

    @classmethod
    def prepare_data_for_logging(cls, instance):
        activities_data = []
        for item in instance.goods_receipt_product_goods_receipt.all():
            warehouse_filter = item.goods_receipt_warehouse_gr_product.all()
            for child in warehouse_filter:
                existed = cls.check_exist(item.product.id, child.warehouse.id, str(instance.id), activities_data)
                if not existed:
                    lot_data = [{
                        'lot_id': str(lot.id),
                        'lot_number': lot.lot_number,
                        'lot_quantity': lot.quantity_import,
                        'lot_value': lot.quantity_import * item.product_unit_price,
                        'lot_expire_date': str(lot.expire_date)
                    } for lot in child.goods_receipt_lot_gr_warehouse.all()]

                    activities_data.append({
                        'product': item.product,
                        'warehouse': child.warehouse,
                        'system_date': instance.date_approved,
                        'posting_date': instance.date_approved,
                        'document_date': instance.date_approved,
                        'stock_type': 1,
                        'trans_id': str(instance.id),
                        'trans_code': instance.code,
                        'trans_title': 'Goods receipt (IA)' if instance.goods_receipt_type == 1 else 'Goods receipt',
                        'quantity': item.quantity_import,
                        'cost': item.product_unit_price,
                        'value': item.product_subtotal_price,
                        'lot_data': lot_data
                    })
                else:
                    existed['quantity'] += item.quantity_import
                    existed['value'] += item.product_unit_price * item.quantity_import
        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_approved,
            activities_data
        )
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
                self.prepare_data_for_logging(self)

            # check if date_approved then call related functions
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    if 'date_approved' in kwargs['update_fields']:
                        GRFinishHandler.push_to_product_warehouse(self)
                        GRFinishHandler.update_product_wait_receipt_amount(self)
                        GRFinishHandler.update_gr_info_for_po(self)
                        GRFinishHandler.update_gr_info_for_ia(self)
                        GRFinishHandler.update_is_all_receipted_po(self)
                        GRFinishHandler.update_is_all_receipted_ia(self)

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
        ordering = ()
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
