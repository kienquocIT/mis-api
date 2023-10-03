from django.db import models
from django.utils import timezone

from apps.shared import DataAbstractModel, MasterDataAbstractModel, REQUEST_FOR, PURCHASE_STATUS


class PurchaseRequest(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="sale_order",
        null=True,
    )

    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="purchase_supplier",
    )
    request_for = models.SmallIntegerField(
        choices=REQUEST_FOR,
        default=0
    )
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        related_name="purchase_contact",
    )

    delivered_date = models.DateTimeField(
        help_text='Deadline for delivery'
    )
    purchase_status = models.SmallIntegerField(
        choices=PURCHASE_STATUS,
        default=0
    )

    note = models.CharField(
        max_length=1000
    )

    purchase_request_product_datas = models.JSONField(
        default=list,
        help_text="read data product, use for get list or detail purchase",
    )

    pretax_amount = models.FloatField(
        help_text='total price of products before tax'
    )

    taxes = models.FloatField(
        help_text='total tax'
    )

    total_price = models.FloatField(
        help_text='total price of products'
    )

    class Meta:
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def update_purchase_status(self):
        products = PurchaseRequestProduct.objects.filter(purchase_request=self)
        is_ordered = True
        for product in products:
            if product.remain_for_purchase_order != 0:
                is_ordered = False
                break
        if is_ordered:
            self.purchase_status = 2
        else:
            self.purchase_status = 1
        self.save(update_fields=['purchase_status'])
        return True

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        purchase_request = PurchaseRequest.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "PR"
        if not self.code:
            temper = "%04d" % (purchase_request + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

        # hit DB
        super().save(*args, **kwargs)


class PurchaseRequestProduct(MasterDataAbstractModel):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="purchase_request",
    )

    sale_order_product = models.ForeignKey(
        'saleorder.SaleOrderProduct',
        on_delete=models.CASCADE,
        related_name="purchase_request_so_product",
        null=True,
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="purchase_request_product",
    )

    description = models.CharField(
        max_length=500,
    )

    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name="purchase_request_uom",
    )

    quantity = models.FloatField()

    unit_price = models.FloatField()

    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        related_name="purchase_request_tax",
    )

    sub_total_price = models.FloatField()

    remain_for_purchase_order = models.FloatField(
        default=0,
        help_text="this is quantity of product which is not purchased order yet, update when PO finish"
    )

    date_modified = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        verbose_name = 'Purchase Request Product'
        verbose_name_plural = 'Purchase Request Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
