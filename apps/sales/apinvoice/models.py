from django.db import models
from apps.accounting.accountingsettings.utils.je_doc_data_log_handler import JEDocDataLogHandler
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
# from apps.sales.reconciliation.utils import ReconForAPInvoiceHandler
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

    # sum_after_fa_increased

    class Meta:
        verbose_name = 'AP Invoice'
        verbose_name_plural = 'AP Invoices'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'c05a6cf4-efff-47e0-afcf-072017b8141a'

    @classmethod
    def update_goods_receipt_has_ap_invoice_already(cls, instance):
        for item in instance.ap_invoice_goods_receipts.all():
            if item.goods_receipt_mapped:
                item.goods_receipt_mapped.has_ap_invoice_already = True
                item.goods_receipt_mapped.save(update_fields=['has_ap_invoice_already'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    self.update_goods_receipt_has_ap_invoice_already(self)
                    JEDocDataLogHandler.push_data_to_je_doc_data(self)
                    # ReconForAPInvoiceHandler.auto_create_recon_doc(self)
        # hit DB
        super().save(*args, **kwargs)


class APInvoiceItems(SimpleAbstractModel):
    ap_invoice = models.ForeignKey('APInvoice', on_delete=models.CASCADE, related_name='ap_invoice_items')
    order = models.IntegerField(default=0)

    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_data = models.JSONField(default=dict)
    product_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    product_uom_data = models.JSONField(default=dict)
    product_quantity = models.FloatField(default=1)
    product_unit_price = models.FloatField(default=0)

    ap_product_des = models.TextField(null=True, blank=True)

    product_subtotal = models.FloatField(default=0)
    product_tax = models.ForeignKey('saledata.Tax', on_delete=models.CASCADE, null=True)
    product_tax_data = models.JSONField(default=dict)
    product_tax_value = models.FloatField(default=0)
    product_subtotal_final = models.FloatField(default=0)
    note = models.TextField(blank=True)
    increased_FA_value = models.FloatField(
        default=0, help_text='increased fixed asset value for this item (product_subtotal)'
    )
    # increased_FA_quantity = models.BooleanField(default=0)

    class Meta:
        verbose_name = 'AP Invoice Item'
        verbose_name_plural = 'AP Invoice Items'
        ordering = ('order',)
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

    @classmethod
    def get_doc_field_name(cls):
        return 'ap_invoice'

    class Meta:
        verbose_name = 'AP Invoice attachment'
        verbose_name_plural = 'AP Invoice attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
