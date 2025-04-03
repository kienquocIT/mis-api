from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import SimpleAbstractModel, DataAbstractModel


INVOICE_EXP = (
    (0, '01GTKT0'),
    (1, '01GTKT3'),
    (2, '02GTTT0'),
    (3, '02GTTT3'),
    (4, '03XKNB3'),
    (5, '04HGDL3'),
    (6, '07KPTQ3'),
)


class APInvoice(DataAbstractModel):
    supplier_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    supplier_mapped_data = models.JSONField(default=dict)
    purchase_order_mapped = models.ForeignKey('purchasing.PurchaseOrder', on_delete=models.CASCADE)
    purchase_order_mapped_data = models.JSONField(default=dict)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    invoice_date = models.DateTimeField()
    invoice_sign = models.CharField(max_length=250, null=True, blank=True)
    invoice_number = models.CharField(max_length=250, null=True, blank=True)
    invoice_example = models.SmallIntegerField(choices=INVOICE_EXP)
    sum_pretax_value = models.FloatField(default=0)
    sum_tax_value = models.FloatField(default=0)
    sum_after_tax_value = models.FloatField(default=0)
    cash_outflow_done = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = 'AP Invoice'
        verbose_name_plural = 'AP Invoices'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def update_goods_receipt_has_ap_invoice_already(cls, instance):
        for item in instance.ap_invoice_goods_receipts.all():
            if item.goods_receipt_mapped:
                item.goods_receipt_mapped.has_ap_invoice_already = True
                item.goods_receipt_mapped.save(update_fields=['has_ap_invoice_already'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'AP[n4]', True)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.update_goods_receipt_has_ap_invoice_already(self)
        # hit DB
        super().save(*args, **kwargs)


class APInvoiceItems(SimpleAbstractModel):
    ap_invoice = models.ForeignKey('APInvoice', on_delete=models.CASCADE, related_name='ap_invoice_items')
    item_index = models.IntegerField(default=0)

    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_data = models.JSONField(default=dict)
    product_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    product_uom_data = models.JSONField(default=dict)
    product_quantity = models.FloatField(default=0)
    product_unit_price = models.FloatField(default=0)
    product_tax = models.ForeignKey('saledata.Tax', on_delete=models.CASCADE, null=True)
    product_tax_data = models.JSONField(default=dict)
    product_tax_value = models.FloatField(default=0)
    product_subtotal_final = models.FloatField(default=0)
    product_subtotal = models.FloatField(default=0)
    note = models.TextField(blank=True)
    increased_FA_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'AP Invoice Item'
        verbose_name_plural = 'AP Invoice Items'
        ordering = ()
        default_permissions = ()
        permissions = ()


class APInvoiceGoodsReceipt(SimpleAbstractModel):
    ap_invoice = models.ForeignKey('APInvoice', on_delete=models.CASCADE, related_name='ap_invoice_goods_receipts')
    goods_receipt_mapped = models.ForeignKey('inventory.GoodsReceipt', on_delete=models.CASCADE)
    goods_receipt_mapped_data = models.JSONField(default=dict)

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
