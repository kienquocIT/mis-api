from django.db import models

from apps.masterdata.saledata.models import ProductWareHouse
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
    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="supplier",
        related_name="goods_receipt_supplier",
        null=True,
        help_text="sale data Accounts have type supplier"
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
            # code = 'GR0001-' + StringHandler.random_str(17)
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
    def update_gr_info_for_po(cls, instance):
        if not instance.inventory_adjustment:
            for gr_po_product in instance.goods_receipt_product_goods_receipt.all():
                gr_po_product.purchase_order_product.gr_completed_quantity += gr_po_product.quantity_import
                gr_po_product.purchase_order_product.gr_completed_quantity = round(
                    gr_po_product.purchase_order_product.gr_completed_quantity,
                    2
                )
                gr_po_product.purchase_order_product.gr_remain_quantity -= gr_po_product.quantity_import
                gr_po_product.purchase_order_product.gr_remain_quantity = round(
                    gr_po_product.purchase_order_product.gr_remain_quantity,
                    2
                )
                gr_po_product.purchase_order_product.save(update_fields=['gr_completed_quantity', 'gr_remain_quantity'])
            for gr_pr_product in instance.goods_receipt_request_product_goods_receipt.all():
                gr_pr_product.purchase_order_request_product.gr_completed_quantity += gr_pr_product.quantity_import
                gr_pr_product.purchase_order_request_product.gr_completed_quantity = round(
                    gr_pr_product.purchase_order_request_product.gr_completed_quantity,
                    2
                )
                gr_pr_product.purchase_order_request_product.gr_remain_quantity -= gr_pr_product.quantity_import
                gr_pr_product.purchase_order_request_product.gr_remain_quantity = round(
                    gr_pr_product.purchase_order_request_product.gr_remain_quantity,
                    2
                )
                gr_pr_product.purchase_order_request_product.save(update_fields=[
                    'gr_completed_quantity',
                    'gr_remain_quantity'
                ])
        return True

    @classmethod
    def update_is_all_receipted_po(cls, instance):
        if instance.purchase_order:
            po_product = instance.purchase_order.purchase_order_product_order.all()
            po_product_done = instance.purchase_order.purchase_order_product_order.filter(gr_remain_quantity=0)
            if po_product.count() == po_product_done.count():
                instance.purchase_order.receipt_status = 3
                instance.purchase_order.is_all_receipted = True
                instance.purchase_order.save(update_fields=['receipt_status', 'is_all_receipted'])
            else:
                instance.purchase_order.receipt_status = 2
                instance.purchase_order.save(update_fields=['receipt_status'])
        return True

    @classmethod
    def push_by_po(cls, instance):
        for gr_warehouse in instance.goods_receipt_warehouse_goods_receipt.all():
            uom_product_inventory = gr_warehouse.goods_receipt_product.product.inventory_uom
            uom_product_gr = gr_warehouse.goods_receipt_product.uom
            if gr_warehouse.goods_receipt_request_product:  # Case has PR
                if gr_warehouse.goods_receipt_request_product.purchase_order_request_product:
                    pr_product = gr_warehouse.goods_receipt_request_product.purchase_order_request_product
                    if pr_product.is_stock is False:  # Case PR is Product
                        if pr_product.purchase_request_product:
                            uom_product_gr = pr_product.purchase_request_product.uom
                    else:  # Case PR is Stock
                        uom_product_gr = pr_product.uom_stock
            final_ratio = 1
            if uom_product_inventory and uom_product_gr:
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
            lot_data = []
            serial_data = []
            for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
                if lot.lot:
                    lot.lot.quantity_import += lot.quantity_import * final_ratio
                    lot.lot.save(update_fields=['quantity_import'])
                else:
                    lot_data.append({
                        'lot_number': lot.lot_number,
                        'quantity_import': lot.quantity_import * final_ratio,
                        'expire_date': lot.expire_date,
                        'manufacture_date': lot.manufacture_date,
                    })
            for serial in gr_warehouse.goods_receipt_serial_gr_warehouse.all():
                serial_data.append({
                    'vendor_serial_number': serial.vendor_serial_number,
                    'serial_number': serial.serial_number,
                    'expire_date': serial.expire_date,
                    'manufacture_date': serial.manufacture_date,
                    'warranty_start': serial.warranty_start,
                    'warranty_end': serial.warranty_end,
                })
            ProductWareHouse.push_from_receipt(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=gr_warehouse.goods_receipt_product.product_id,
                warehouse_id=gr_warehouse.warehouse_id,
                uom_id=uom_product_inventory.id,
                tax_id=gr_warehouse.goods_receipt_product.product.purchase_tax_id,
                amount=gr_warehouse.quantity_import * final_ratio,
                unit_price=gr_warehouse.goods_receipt_product.product_unit_price,
                lot_data=lot_data,
                serial_data=serial_data,
            )
        return True

    @classmethod
    def push_by_ia(cls, instance):
        for gr_warehouse in instance.goods_receipt_warehouse_goods_receipt.all():
            uom_product_inventory = gr_warehouse.goods_receipt_product.product.inventory_uom
            uom_product_gr = gr_warehouse.goods_receipt_product.uom
            final_ratio = 1
            if uom_product_inventory and uom_product_gr:
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
            lot_data = []
            serial_data = []
            for lot in gr_warehouse.goods_receipt_lot_gr_warehouse.all():
                if lot.lot:  # if GR for exist LOT => update quantity
                    lot.lot.quantity_import += lot.quantity_import * final_ratio
                    lot.lot.save(update_fields=['quantity_import'])
                else:  # GR with new LOTS => setup data to create ProductWarehouseLot
                    lot_data.append({
                        'lot_number': lot.lot_number,
                        'quantity_import': lot.quantity_import * final_ratio,
                        'expire_date': lot.expire_date,
                        'manufacture_date': lot.manufacture_date,
                    })
            for serial in gr_warehouse.goods_receipt_serial_gr_warehouse.all():
                serial_data.append({
                    'vendor_serial_number': serial.vendor_serial_number,
                    'serial_number': serial.serial_number,
                    'expire_date': serial.expire_date,
                    'manufacture_date': serial.manufacture_date,
                    'warranty_start': serial.warranty_start,
                    'warranty_end': serial.warranty_end,
                })
            ProductWareHouse.push_from_receipt(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                product_id=gr_warehouse.goods_receipt_product.product_id,
                warehouse_id=gr_warehouse.warehouse_id,
                uom_id=uom_product_inventory.id,
                tax_id=gr_warehouse.goods_receipt_product.product.purchase_tax_id,
                amount=gr_warehouse.goods_receipt_product.quantity_import * final_ratio,
                unit_price=gr_warehouse.goods_receipt_product.product_unit_price,
                lot_data=lot_data,
                serial_data=serial_data,
            )
        return True

    @classmethod
    def push_to_product_warehouse(cls, instance):
        # push data to ProductWareHouse
        if instance.goods_receipt_type == 0:  # GR for PO
            cls.push_by_po(instance=instance)
        elif instance.goods_receipt_type == 1:  # GR for IA
            cls.push_by_ia(instance=instance)
        return True

    @classmethod
    def update_product_wait_receipt_amount(cls, instance):
        if instance.purchase_order:  # GR for PO
            for product_receipt in instance.goods_receipt_product_goods_receipt.all():
                uom_product_inventory = product_receipt.product.inventory_uom
                uom_product_gr = product_receipt.uom
                final_ratio = 1
                if uom_product_inventory and uom_product_gr:
                    final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
                product_receipt.product.save(**{
                    'update_transaction_info': True,
                    'quantity_receipt_po': product_receipt.quantity_import * final_ratio,
                    'update_fields': ['wait_receipt_amount', 'available_amount', 'stock_amount']
                })
        else:  # GR for IA
            for product_receipt in instance.goods_receipt_product_goods_receipt.all():
                uom_product_inventory = product_receipt.product.inventory_uom
                uom_product_gr = product_receipt.uom
                final_ratio = 1
                if uom_product_inventory and uom_product_gr:
                    final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
                product_receipt.product.save(**{
                    'update_transaction_info': True,
                    'quantity_receipt_ia': product_receipt.quantity_import * final_ratio,
                    'update_fields': ['available_amount', 'stock_amount']
                })
        return True

    @classmethod
    def prepare_data_for_logging(cls, instance):
        activities_data = []
        for item in instance.goods_receipt_warehouse_goods_receipt.all():
            activities_data.append({
                'product': item.goods_receipt_product.product,
                'warehouse': item.warehouse,
                'system_date': instance.date_approved,
                'posting_date': None,
                'document_date': None,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'quantity': item.quantity_import,
                'cost': item.goods_receipt_product.product_unit_price,
                'value': item.goods_receipt_product.product_unit_price * item.quantity_import,
            })
        ReportInventorySub.logging_when_stock_activities_happened(
            instance.date_approved,
            activities_data
        )
        return True

    def save(self, *args, **kwargs):
        # if self.system_status == 2:  # added
        if self.system_status in [2, 3]:  # added, finish
            # check if not code then generate code
            if not self.code:
                self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.prepare_data_for_logging(self)

            # check if date_approved then call related functions
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    if 'date_approved' in kwargs['update_fields']:
                        self.push_to_product_warehouse(self)
                        self.update_product_wait_receipt_amount(self)
                        self.update_gr_info_for_po(self)
                        self.update_is_all_receipted_po(self)

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
