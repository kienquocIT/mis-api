from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import (
    SimpleAbstractModel, DataAbstractModel
)
# Create your models here.


INVOICE_EXP = (
    (0, '01GTKT0/001'),
    (1, '01GTKT3/001'),
    (2, '02GTTT0/001'),
    (3, '02GTTT3/001'),
    (4, '03XKNB3/001'),
    (5, '04HGDL3/001'),
    (6, '07KPTQ3/001'),
)


class ARInvoice(DataAbstractModel):
    customer_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=250, null=True, blank=True)
    sale_order_mapped = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    invoice_date = models.DateTimeField()
    invoice_sign = models.CharField(max_length=250)
    invoice_number = models.CharField(max_length=250)
    invoice_example = models.SmallIntegerField(choices=INVOICE_EXP)

    class Meta:
        verbose_name = 'AR Invoice'
        verbose_name_plural = 'AR Invoices'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ARInvoiceItems(SimpleAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_items')
    item_index = models.IntegerField(default=0)

    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    product_quantity = models.FloatField(default=0)
    product_unit_price = models.FloatField(default=0)
    product_subtotal = models.FloatField(default=0)
    product_discount_rate = models.FloatField(default=0)
    product_discount_value = models.FloatField(default=0)
    product_tax_rate = models.FloatField(default=0)
    product_tax_title = models.CharField(max_length=100, blank=True)
    product_tax_value = models.FloatField(default=0)

    product_subtotal_final = models.FloatField(default=0)

    class Meta:
        verbose_name = 'AR Invoice Item'
        verbose_name_plural = 'AR Invoice Items'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ARInvoiceDelivery(SimpleAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_deliveries')
    delivery_mapped = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'AR Invoice Delivery'
        verbose_name_plural = 'AR Invoice Deliveries'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ARInvoiceAttachmentFile(M2MFilesAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_attachments')

    class Meta:
        verbose_name = 'AR Invoice attachment'
        verbose_name_plural = 'AR Invoice attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
