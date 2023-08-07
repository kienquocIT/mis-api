from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel


LEAD_TIME_TYPE = [
    (1, _('Week')),
    (2, _('Day')),
    (3, _('Hour')),
]


class PurchaseQuotation(DataAbstractModel):
    supplier_mapped = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE
    )
    contact_mapped = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE
    )
    purchase_quotation_request_mapped = models.ForeignKey(
        'purchasing.PurchaseQuotationRequest',
        null=True,
        on_delete=models.CASCADE
    )
    expiration_date = models.DateTimeField(
        help_text='Deadline for delivery'
    )
    lead_time_from = models.FloatField()
    lead_time_to = models.FloatField()
    lead_time_type = models.SmallIntegerField(
        choices=LEAD_TIME_TYPE
    )
    note = models.CharField(
        max_length=1000
    )
    pretax_price = models.FloatField(
        help_text='sum pretax price of products',
    )

    taxes_price = models.FloatField(
        help_text='sum taxes price of products',
    )

    total_price = models.FloatField(
        help_text='sum after tax price of products',
    )

    class Meta:
        verbose_name = 'Purchase Quotation'
        verbose_name_plural = 'Purchase Quotations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class PurchaseQuotationProduct(SimpleAbstractModel):
    purchase_quotation = models.ForeignKey(
        PurchaseQuotation,
        on_delete=models.CASCADE,
        related_name="purchase_quotation",
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="purchase_quotation_product",
    )

    description = models.CharField(
        max_length=500,
    )

    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name="purchase_quotation_product_uom",
    )

    quantity = models.IntegerField()

    unit_price = models.FloatField()

    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        related_name="purchase_quotation_product_tax",
    )

    subtotal_price = models.FloatField()

    class Meta:
        verbose_name = 'Purchase Quotation Product'
        verbose_name_plural = 'Purchase Quotation Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
