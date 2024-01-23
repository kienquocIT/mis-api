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


class APInvoice(DataAbstractModel):
    supplier_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    supplier_name = models.CharField(max_length=250, null=True, blank=True)
    po_mapped = models.ForeignKey('purchasing.PurchaseOrder', on_delete=models.CASCADE)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    invoice_date = models.DateTimeField()
    invoice_sign = models.CharField(max_length=250)
    invoice_number = models.CharField(max_length=250)
    invoice_example = models.SmallIntegerField(choices=INVOICE_EXP)

    class Meta:
        verbose_name = 'AP Invoice'
        verbose_name_plural = 'AP Invoices'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class APInvoiceItems(SimpleAbstractModel):
    ap_invoice = models.ForeignKey('APInvoice', on_delete=models.CASCADE, related_name='ap_invoice_items')
    item_index = models.IntegerField(default=0)

    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    product_quantity = models.FloatField(default=0)
    product_unit_price = models.FloatField(default=0)
    product_tax_value = models.FloatField(default=0)
    product_subtotal = models.FloatField(default=0)

    class Meta:
        verbose_name = 'AP Invoice Item'
        verbose_name_plural = 'AP Invoice Items'
        ordering = ()
        default_permissions = ()
        permissions = ()


class APInvoiceGoodsReceipt(SimpleAbstractModel):
    ap_invoice = models.ForeignKey('APInvoice', on_delete=models.CASCADE, related_name='ap_invoice_goods_receipt')
    goods_receipt_mapped = models.ForeignKey('inventory.GoodsReceipt', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'AP Invoice Goods Receipt'
        verbose_name_plural = 'AP Invoice Goods Receipt'
        ordering = ()
        default_permissions = ()
        permissions = ()


class APInvoiceAttachmentFile(M2MFilesAbstractModel):
    ap_invoice = models.ForeignKey('APInvoice', on_delete=models.CASCADE, related_name='ap_invoice_attachments')

    class Meta:
        verbose_name = 'AP Invoice attachment'
        verbose_name_plural = 'AP Invoice attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
