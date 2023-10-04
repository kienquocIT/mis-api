from django.db import models

from apps.masterdata.saledata.models import ProductWareHouse
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
    def push_to_product_warehouse(cls, gr_obj):
        # push data to ProductWareHouse
        if gr_obj.goods_receipt_type == 0:  # GR for PO
            for gr_warehouse in GoodsReceiptWarehouse.objects.filter(goods_receipt=gr_obj):
                uom_product_inventory = \
                    gr_warehouse.goods_receipt_request_product.goods_receipt_product.product.inventory_uom
                uom_product_gr = gr_warehouse.goods_receipt_request_product.goods_receipt_product.uom
                final_ratio = uom_product_gr.ratio / uom_product_inventory.ratio
                ProductWareHouse.push_from_receipt(
                    tenant_id=gr_obj.tenant_id,
                    company_id=gr_obj.company_id,
                    product_id=gr_warehouse.goods_receipt_request_product.goods_receipt_product.product_id,
                    warehouse_id=gr_warehouse.warehouse_id,
                    uom_id=uom_product_inventory.id,
                    tax_id=gr_warehouse.goods_receipt_request_product.goods_receipt_product.tax_id,
                    amount=gr_warehouse.quantity_import * final_ratio,
                    unit_price=gr_warehouse.goods_receipt_request_product.goods_receipt_product.product_unit_price,
                )
        elif gr_obj.goods_receipt_type == 1:  # GR for IA
            for gr_product in GoodsReceiptProduct.objects.filter(goods_receipt=gr_obj):
                ProductWareHouse.push_from_receipt(
                    tenant_id=gr_obj.tenant_id,
                    company_id=gr_obj.company_id,
                    product_id=gr_product.product_id,
                    warehouse_id=gr_product.warehouse_id,
                    uom_id=gr_product.product.inventory_uom_id,
                    tax_id=gr_product.tax_id,
                    amount=gr_product.quantity_import,
                    unit_price=gr_product.product_unit_price,
                )
        return True

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        goods_receipt = GoodsReceipt.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "GR"
        if not self.code:
            temper = "%04d" % (goods_receipt + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

        if self.system_status in [2, 3]:
            self.push_to_product_warehouse(self)
            # update receipt status to PurchaseOrder

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
    purchase_request_product = models.ForeignKey(
        'purchasing.PurchaseRequestProduct',
        on_delete=models.CASCADE,
        verbose_name="purchase request product",
        related_name="goods_receipt_request_product_pr_product",
        null=True
    )
    quantity_import = models.FloatField(default=0)

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
