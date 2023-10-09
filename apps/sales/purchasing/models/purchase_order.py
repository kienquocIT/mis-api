from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel, RECEIPT_STATUS, StringHandler


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
    purchase_request_products_data = models.JSONField(
        default=list,
        help_text="read data purchase request products not map any PO, use for get list or detail"
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
    total_product_pretax_amount = models.FloatField(
        default=0,
        help_text="total pretax amount of tab product"
    )
    total_product_tax = models.FloatField(
        default=0,
        help_text="total tax of tab product"
    )
    total_product = models.FloatField(
        default=0,
        help_text="total amount of tab product"
    )
    total_product_revenue_before_tax = models.FloatField(
        default=0,
        help_text="total revenue before tax of tab product (after discount on total, apply promotion,...)"
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
            code = 'PO0001-' + StringHandler.random_str(17)
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
        list_purchase_request = []
        # update quantity remain on purchase request product
        for po_request in PurchaseOrderRequestProduct.objects.filter(purchase_order=instance):
            po_request.purchase_request_product.remain_for_purchase_order -= po_request.quantity_order
            if po_request.purchase_request_product.purchase_request not in list_purchase_request:
                list_purchase_request.append(po_request.purchase_request_product.purchase_request)
            po_request.purchase_request_product.save(update_fields=['remain_for_purchase_order'])
        for purchase_request in list_purchase_request:
            purchase_request.update_purchase_status()
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
            self.update_remain_and_status_purchase_request(self)

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
    is_use = models.BooleanField(
        default=False,
        help_text='purchase quotation that used to order',
    )

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
    stock = models.FloatField(
        default=0,
        help_text='quantity of product in stock',
    )
    # product information
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
    product_tax_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    product_subtotal_price = models.FloatField(
        default=0
    )
    product_subtotal_price_after_tax = models.FloatField(
        default=0
    )
    order = models.IntegerField(
        default=1
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
    # quantity_remain = models.FloatField(
    #     default=0,
    #     help_text='quantity remain to order',
    # )

    class Meta:
        verbose_name = 'Purchase Order Request Product'
        verbose_name_plural = 'Purchase Order Request Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
