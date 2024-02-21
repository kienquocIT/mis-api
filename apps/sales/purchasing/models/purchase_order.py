from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.sales.report.models import ReportCashflow
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
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        verbose_name="contact",
        related_name="purchase_order_contact",
        null=True
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
    # total amount of products
    total_product_pretax_amount = models.FloatField(default=0, help_text="total pretax amount of tab product")
    total_product_tax = models.FloatField(default=0, help_text="total tax of tab product")
    total_product = models.FloatField(default=0, help_text="total amount of tab product")
    total_product_revenue_before_tax = models.FloatField(
        default=0,
        help_text="total revenue before tax of tab product (after discount on total, apply promotion,...)"
    )
    is_all_receipted = models.BooleanField(
        default=False,
        help_text="True if all products are receipted by Goods Receipt"
    )
    purchase_order_payment_stage = models.JSONField(
        default=list,
        help_text="read data payment stage, use for get list or detail purchase order"
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
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("PO")[1])
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
            # code = 'PO0001-' + StringHandler.random_str(17)
            code = 'PO0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'PO{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def update_remain_and_status_purchase_request(cls, instance):
        # update quantity remain on purchase request product
        for po_request in instance.purchase_order_request_product_order.filter(is_stock=False):
            po_request.purchase_request_product.remain_for_purchase_order -= po_request.quantity_order
            po_request.purchase_request_product.save(update_fields=['remain_for_purchase_order'])
        return True

    @classmethod
    def update_is_all_ordered_purchase_request(cls, instance):
        for pr_obj in instance.purchase_requests.all():
            pr_product = pr_obj.purchase_request.all()
            pr_product_done = pr_obj.purchase_request.filter(remain_for_purchase_order=0)
            if pr_product.count() == pr_product_done.count():  # All PR products ordered
                pr_obj.purchase_status = 2
                pr_obj.is_all_ordered = True
                pr_obj.save(update_fields=['purchase_status', 'is_all_ordered'])
            else:  # Partial PR products ordered
                pr_obj.purchase_status = 1
                pr_obj.save(update_fields=['purchase_status'])
        return True

    @classmethod
    def update_product_wait_receipt_amount(cls, instance):
        for product_purchase in instance.purchase_order_product_order.all():
            uom_product_inventory = product_purchase.product.inventory_uom
            uom_product_po = product_purchase.uom_order_actual
            if product_purchase.uom_order_request:
                uom_product_po = product_purchase.uom_order_request
            final_ratio = 1
            if uom_product_inventory and uom_product_po:
                final_ratio = uom_product_po.ratio / uom_product_inventory.ratio
            product_quantity_order_request_final = product_purchase.product_quantity_order_actual* final_ratio
            if instance.purchase_requests.exists():
                product_quantity_order_request_final = product_purchase.product_quantity_order_request * final_ratio
            stock_final = product_purchase.stock * final_ratio
            product_purchase.product.save(**{
                'update_transaction_info': True,
                'quantity_purchase': product_quantity_order_request_final + stock_final,
                'update_fields': ['wait_receipt_amount', 'available_amount']
            })
        return True

    @classmethod
    def push_to_report_cashflow(cls, instance):
        po_products_json = {}
        po_products = instance.purchase_order_product_order.all()
        for po_product in po_products:
            if str(po_product.product_id) not in po_products_json:
                po_products_json.update({str(po_product.product_id): {
                    'po': str(po_product.purchase_order_id),
                    'quantity': po_product.product_quantity_order_actual,
                }})
        po_purchase_requests = instance.purchase_requests.filter(sale_order__isnull=False)
        for purchase_request in po_purchase_requests:
            so_rate = 0
            for pr_product in purchase_request.purchase_request.all():
                if str(pr_product.product_id) in po_products_json:
                    po_product_map = po_products_json[str(pr_product.product_id)]
                    so_rate += (po_product_map.get('quantity', 0) / pr_product.quantity) * 100
            so_rate = min(so_rate, 100)
            # payment
            bulk_data = [ReportCashflow(
                tenant_id=purchase_request.sale_order.tenant_id,
                company_id=purchase_request.sale_order.company_id,
                sale_order_id=purchase_request.sale_order_id,
                purchase_order_id=instance.id,
                cashflow_type=3,
                employee_inherit_id=purchase_request.sale_order.employee_inherit_id,
                group_inherit_id=purchase_request.sale_order.employee_inherit.group_id,
                due_date=payment_stage.due_date,
                # value_estimate_cost=payment_stage.value_before_tax * so_rate / 100,
                value_estimate_cost=payment_stage.value_before_tax,
            ) for payment_stage in instance.purchase_order_payment_stage_po.all()]
            ReportCashflow.push_from_so_po(bulk_data)
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
            # check if date_approved then call related functions
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    if 'date_approved' in kwargs['update_fields']:
                        self.update_remain_and_status_purchase_request(self)
                        self.update_is_all_ordered_purchase_request(self)
                        self.update_product_wait_receipt_amount(self)
                        # report
                        self.push_to_report_cashflow(self)

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
    product_title = models.CharField(max_length=100, blank=True, null=True)
    product_code = models.CharField(max_length=100, blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
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
    product_tax_title = models.CharField(max_length=100, blank=True, null=True)
    product_tax_amount = models.FloatField(default=0)
    product_subtotal_price = models.FloatField(default=0)
    product_subtotal_price_after_tax = models.FloatField(default=0)
    order = models.IntegerField(default=1)
    # goods receipt information
    gr_completed_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is goods receipted, update when GR finish"
    )
    gr_remain_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not goods receipted yet, update when GR finish"
    )

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
    # goods receipt information
    gr_completed_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is goods receipted, update when GR finish"
    )
    gr_remain_quantity = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not goods receipted yet, update when GR finish"
    )

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
    payment_ratio = models.FloatField(default=0)
    value_before_tax = models.FloatField(default=0)
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="tax",
        related_name="purchase_order_payment_stage_tax",
        null=True
    )
    value_after_tax = models.FloatField(default=0)
    due_date = models.DateTimeField(null=True)
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Purchase Order Payment Stage'
        verbose_name_plural = 'Purchase Order Payment Stages'
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
