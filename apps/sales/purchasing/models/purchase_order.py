from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.purchasing.utils import POHandler, POFinishHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel, RECEIPT_STATUS, MasterDataAbstractModel


class PurchaseOrder(DataAbstractModel):
    purchase_requests = models.ManyToManyField(
        'purchasing.PurchaseRequest',
        through="PurchaseOrderRequest",
        symmetrical=False,
        blank=True,
        related_name='purchase_order_map_request'
    )
    purchase_requests_data = models.JSONField(
        default=list,
        help_text="read data purchase requests, use for get list or detail"
    )
    purchase_quotations = models.ManyToManyField(
        'purchasing.PurchaseQuotation',
        through="PurchaseOrderQuotation",
        symmetrical=False,
        blank=True,
        related_name='purchase_order_map_quotation'
    )
    purchase_quotations_data = models.JSONField(
        default=list,
        help_text="read data purchase quotations, use for get list or detail"
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="supplier",
        related_name="purchase_order_supplier",
        null=True,
        help_text="sale data Accounts have type supplier"
    )
    supplier_data = models.JSONField(
        default=dict,
        help_text="read data supplier, use for get list or detail"
    )
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="contact",
        related_name="purchase_order_contact",
        null=True
    )
    contact_data = models.JSONField(
        default=dict,
        help_text="read data contact, use for get list or detail"
    )
    delivered_date = models.DateTimeField(
        null=True,
        help_text='date that products will be delivered',
    )
    status_delivered = models.SmallIntegerField(default=0)
    receipt_status = models.SmallIntegerField(
        choices=RECEIPT_STATUS,
        default=0
    )
    # tab products
    purchase_order_products_data = models.JSONField(
        default=list,
        help_text="read data products, use for get list or detail"
    )
    purchase_order_payment_stage = models.JSONField(
        default=list,
        help_text="read data payment stage, use for get list or detail purchase order"
    )
    purchase_order_invoice = models.JSONField(
        default=list,
        help_text="read data invoice, use for get list or detail purchase order"
    )
    # total amount of products
    total_product_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab product")
    total_product_tax = models.FloatField(default=0, help_text="total tax of tab product")
    total_product = models.FloatField(default=0, help_text="total amount of tab product")
    total_product_revenue_before_tax = models.FloatField(
        default=0,
        help_text="total revenue before tax of tab product (after discount on total, apply promotion,...)"
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='PurchaseOrderAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='file_of_purchase_order',
    )

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_change_document(cls, instance):
        if not instance:
            return False
        return True

    @classmethod
    def check_reject_document(cls, instance):
        # check if there is CR not done
        if cls.objects.filter_on_company(document_root_id=instance.document_root_id, system_status__in=[1, 2]).exists():
            return False
        # check if PO was used for GR
        if instance.goods_receipt_po.filter(system_status__in=[1, 2, 3]).exists():
            return False
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('purchaseorder', True, self, kwargs)
                    POFinishHandler.update_remain_and_status_purchase_request(instance=self)
                    POFinishHandler.update_is_all_ordered_purchase_request(instance=self)
                    POFinishHandler.push_product_info(instance=self)
                    POFinishHandler.push_to_report_cashflow(instance=self)  # report
                    POFinishHandler.push_to_payment_plan(instance=self)  # payment plan

        if self.system_status in [4]:  # cancel
            POFinishHandler.push_product_info(instance=self)

        # diagram
        POHandler.push_diagram(instance=self)
        # hit DB
        super().save(*args, **kwargs)


class PurchaseOrderRequest(SimpleAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="purchase_order_request_order",
    )
    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE,
        verbose_name="purchase request",
        related_name="purchase_order_request_request",
    )

    class Meta:
        verbose_name = 'Purchase Order Request'
        verbose_name_plural = 'Purchase Order Requests'
        ordering = ()
        default_permissions = ()
        permissions = ()


class PurchaseOrderQuotation(SimpleAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="purchase_order_quotation_order",
    )
    purchase_quotation = models.ForeignKey(
        'purchasing.PurchaseQuotation',
        on_delete=models.CASCADE,
        verbose_name="purchase quotation",
        related_name="purchase_order_quotation_quotation",
    )
    is_use = models.BooleanField(default=False, help_text='purchase quotation that used to order')

    class Meta:
        verbose_name = 'Purchase Order Quotation'
        verbose_name_plural = 'Purchase Order Quotations'
        ordering = ()
        default_permissions = ()
        permissions = ()


class PurchaseOrderProduct(SimpleAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="purchase_order_product_order",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="purchase_order_product_product",
        null=True
    )
    uom_order_request = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit of product order on request",
        related_name="purchase_order_product_uom_request",
        null=True
    )
    uom_order_actual = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit of product order actual",
        related_name="purchase_order_product_uom_order",
        null=True
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        null=True
    )
    stock = models.FloatField(default=0, help_text='quantity of product in stock')
    # product information
    product_title = models.CharField(max_length=100, blank=True)
    product_code = models.CharField(max_length=100, blank=True)
    product_description = models.TextField(blank=True)
    product_quantity_order_request = models.FloatField(
        default=0,
        help_text='quantity of product, UI get default by purchase request',
    )
    product_quantity_order_actual = models.FloatField(
        default=0,
        help_text='quantity of product, UI get default by purchase request',
    )
    product_unit_price = models.FloatField(
        default=0,
        help_text='price of product, UI get default by supplier price',
    )
    product_tax_title = models.CharField(max_length=100, blank=True)
    product_tax_amount = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    # fields for receipt
    gr_remain_quantity = models.FloatField(default=0, help_text="minus when receipt")
    # shipping
    is_shipping = models.BooleanField(default=False, help_text="flag to know this record is shipping not product")
    shipping_title = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Purchase Order Product'
        verbose_name_plural = 'Purchase Order Products'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class PurchaseOrderRequestProduct(SimpleAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="purchase_order_request_product_order",
        null=True
    )
    purchase_request_product = models.ForeignKey(
        'purchasing.PurchaseRequestProduct',
        on_delete=models.CASCADE,
        verbose_name="purchase request product",
        related_name="purchase_order_request_request_product",
        null=True,
    )
    purchase_order_product = models.ForeignKey(
        PurchaseOrderProduct,
        on_delete=models.CASCADE,
        verbose_name="purchase order product",
        related_name="purchase_order_request_order_product",
        null=True,
    )
    sale_order_product = models.ForeignKey(
        'saleorder.SaleOrderProduct',
        on_delete=models.CASCADE,
        related_name="purchase_order_request_so_product",
        null=True,
    )
    quantity_order = models.FloatField(
        default=0,
        help_text='quantity order',
    )
    uom_stock = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="unit of measure",
        related_name="purchase_order_request_uom_stock",
        null=True
    )
    is_stock = models.BooleanField(
        default=False,
        help_text="True if quantity order > quantity request => create quantity stock"
    )
    # fields for receipt
    gr_remain_quantity = models.FloatField(default=0, help_text="minus when receipt")

    class Meta:
        verbose_name = 'Purchase Order Request Product'
        verbose_name_plural = 'Purchase Order Request Products'
        ordering = ()
        default_permissions = ()
        permissions = ()


# SUPPORT PAYMENT TERM STAGE
class PurchaseOrderPaymentStage(MasterDataAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="purchase_order_payment_stage_po",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    date_type = models.CharField(max_length=200, blank=True)
    ratio = models.FloatField(null=True)
    invoice = models.IntegerField(null=True)
    invoice_data = models.JSONField(default=dict, help_text='data json of invoice')
    value_before_tax = models.FloatField(default=0)
    value_reconcile = models.FloatField(default=0)
    reconcile_data = models.JSONField(default=list, help_text='data json of reconcile')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="purchase_order_payment_stage_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    value_tax = models.FloatField(default=0)
    value_total = models.FloatField(default=0)
    is_ap_invoice = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    cash_outflow_done = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Purchase Order Payment Stage'
        verbose_name_plural = 'Purchase Order Payment Stages'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class PurchaseOrderInvoice(MasterDataAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name="purchase order",
        related_name="purchase_order_invoice_purchase_order",
    )
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True)
    date = models.DateTimeField(null=True)
    ratio = models.FloatField(null=True)
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="purchase_order_invoice_tax",
        null=True
    )
    tax_data = models.JSONField(default=dict, help_text='data json of tax')
    total = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Purchase Order Invoice'
        verbose_name_plural = 'Purchase Order Invoices'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class PurchaseOrderAttachmentFile(M2MFilesAbstractModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        verbose_name='purchase order',
        related_name="po_attachment_file_po"
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'purchase_order'

    class Meta:
        verbose_name = 'Purchase order attachments'
        verbose_name_plural = 'Purchase order attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
