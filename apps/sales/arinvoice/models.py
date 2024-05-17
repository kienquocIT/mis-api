from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.sales.acceptance.models import FinalAcceptance
from apps.shared import SimpleAbstractModel, DataAbstractModel
# Create your models here.


INVOICE_EXP = (
    (0, '01GTKT0'),
    (1, '01GTKT3'),
    (2, '02GTTT0'),
    (3, '02GTTT3'),
    (4, '03XKNB3'),
    (5, '04HGDL3'),
    (6, '07KPTQ3'),
)

INVOICE_METHOD = (
    (1, 'TM'),
    (2, 'CK'),
    (3, 'TM/CK'),
)

INVOICE_STATUS = (
    (0, _('Created')),  # Khởi tạo
    (1, _('Published')),  # Đã phát hành
    (2, _('Enumerated')),  # Đã kê khai
    (3, _('Replaced')),  # Đã thay thế
    (4, _('Adjusted')),  # Đã điều chỉnh
)


class ARInvoice(DataAbstractModel):
    customer_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    sale_order_mapped = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE, null=True)
    posting_date = models.DateTimeField(null=True)
    document_date = models.DateTimeField(null=True)
    invoice_date = models.DateTimeField(null=True)
    invoice_sign = models.CharField(max_length=250, null=True, blank=True)
    invoice_number = models.CharField(max_length=250, null=True, blank=True)
    invoice_example = models.SmallIntegerField(choices=INVOICE_EXP)
    invoice_method = models.SmallIntegerField(choices=INVOICE_METHOD, default=3)
    invoice_status = models.SmallIntegerField(choices=INVOICE_STATUS, default=0)

    is_free_input = models.BooleanField(default=False)
    # for free input
    customer_code = models.CharField(max_length=50, null=True, blank=True)
    customer_name = models.CharField(max_length=250, null=True, blank=True)
    buyer_name = models.CharField(max_length=250, null=True, blank=True)
    customer_tax_number = models.CharField(max_length=250, null=True, blank=True)
    customer_billing_address = models.CharField(max_length=250, null=True, blank=True)
    customer_bank_code = models.CharField(max_length=50, null=True, blank=True)
    customer_bank_number = models.CharField(max_length=250, null=True, blank=True)

    is_created_einvoice = models.BooleanField(default=False)

    @classmethod
    def push_final_acceptance_invoice(cls, instance):
        sale_order_id = None
        opportunity_id = None
        if instance.sale_order_mapped:
            sale_order_id = instance.sale_order_mapped_id
            opportunity_id = instance.sale_order_mapped.opportunity_id
        if sale_order_id:
            list_data_indicator = []
            for invoice_item in instance.ar_invoice_items.all():
                list_data_indicator.append({
                    'tenant_id': instance.tenant_id,
                    'company_id': instance.company_id,
                    'ar_invoice_id': instance.id,
                    'product_id': invoice_item.product_id if invoice_item.product else None,
                    'actual_value': invoice_item.product_subtotal,
                    'actual_value_after_tax': invoice_item.product_subtotal_final,
                    'acceptance_affect_by': 5,
                })
            FinalAcceptance.push_final_acceptance(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                sale_order_id=sale_order_id,
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                opportunity_id=opportunity_id,
                list_data_indicator=list_data_indicator,
            )
        return True

    def save(self, *args, **kwargs):
        if self.invoice_status == 1:  # published
            self.push_final_acceptance_invoice(instance=self)
        # hit DB
        super().save(*args, **kwargs)

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
    product_tax = models.ForeignKey('saledata.Tax', on_delete=models.CASCADE, null=True)
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


class ARInvoiceSign(SimpleAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)
    company = models.OneToOneField('company.Company', on_delete=models.CASCADE)
    one_vat_sign = models.CharField(max_length=50, null=True, blank=True)
    many_vat_sign = models.CharField(max_length=50, null=True, blank=True)
    sale_invoice_sign = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'AR Invoice Sign'
        verbose_name_plural = 'AR Invoice Signs'
        ordering = ()
        default_permissions = ()
        permissions = ()
