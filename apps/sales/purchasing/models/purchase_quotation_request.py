from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel

PURCHASE_QUOTATION_REQUEST_TYPE = [
    (0, _('From PR')),
    (1, _('Manual')),
]


class PurchaseQuotationRequest(DataAbstractModel):
    purchase_quotation_request_type = models.SmallIntegerField(
        choices=PURCHASE_QUOTATION_REQUEST_TYPE,
        default=0
    )

    delivered_date = models.DateTimeField(
        help_text='Deadline for delivery'
    )

    response_status = models.SmallIntegerField(
        default=0
    )

    note = models.CharField(
        max_length=1000
    )

    pretax_price = models.FloatField(
        help_text='sum pretax price of products'
    )

    taxes_price = models.FloatField(
        help_text='sum taxes price of products'
    )

    total_price = models.FloatField(
        help_text='sum after tax price of products'
    )

    purchase_request_mapped = models.ManyToManyField(
        'purchasing.PurchaseRequest',
        through='PurchaseQuotationRequestPurchaseRequest',
        symmetrical=False,
        blank=True,
        related_name='purchase_request_mapped'
    )

    class Meta:
        verbose_name = 'Purchase Quotation Request'
        verbose_name_plural = 'Purchase Quotation Requests'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class PurchaseQuotationRequestPurchaseRequest(SimpleAbstractModel):
    purchase_quotation_request = models.ForeignKey(
        PurchaseQuotationRequest,
        on_delete=models.CASCADE,
    )

    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Purchase Quotation Request Mapped Purchase Request'
        verbose_name_plural = 'Purchase Quotation Requests Mapped Purchase Requests'
        ordering = ()
        default_permissions = ()
        permissions = ()


class PurchaseQuotationRequestProduct(SimpleAbstractModel):
    purchase_quotation_request = models.ForeignKey(
        PurchaseQuotationRequest,
        on_delete=models.CASCADE,
        related_name="purchase_quotation_request",
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="purchase_quotation_request_product",
    )

    description = models.CharField(
        max_length=500,
    )

    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name="purchase_quotation_request_product_uom",
    )

    quantity = models.IntegerField()

    unit_price = models.FloatField()

    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        related_name="purchase_quotation_request_product_tax",
    )

    subtotal_price = models.FloatField()

    class Meta:
        verbose_name = 'Purchase Quotation Request Product'
        verbose_name_plural = 'Purchase Quotation Requests Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
