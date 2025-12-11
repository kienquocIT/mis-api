from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounting.accountingsettings.utils.je_doc_data_log_handler import JEDocDataLogHandler
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.acceptance.models import FinalAcceptance
# from apps.sales.reconciliation.utils.autocreate_recon_for_ar_invoice import ReconForARInvoiceHandler
from apps.shared import SimpleAbstractModel, DataAbstractModel, RecurrenceAbstractModel


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
)

INVOICE_STATUS = (
    (0, _('Created')),  # Khởi tạo
    (1, _('Published')),  # Đã phát hành
    (2, _('Enumerated')),  # Đã kê khai
    (3, _('Replaced')),  # Đã thay thế
    (4, _('Adjusted')),  # Đã điều chỉnh
)


class ARInvoice(DataAbstractModel, RecurrenceAbstractModel):
    customer_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    customer_mapped_data = models.JSONField(default=dict)
    sale_order_mapped = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE, null=True)
    sale_order_mapped_data = models.JSONField(default=dict)
    lease_order_mapped = models.ForeignKey('leaseorder.LeaseOrder', on_delete=models.CASCADE, null=True)
    lease_order_mapped_data = models.JSONField(default=dict)
    company_bank_account = models.ForeignKey('saledata.BankAccount', on_delete=models.SET_NULL, null=True)
    company_bank_account_data = models.JSONField(default=dict)
    posting_date = models.DateTimeField(null=True)
    document_date = models.DateTimeField(null=True)
    invoice_date = models.DateTimeField(null=True)
    invoice_sign = models.CharField(max_length=250, null=True, blank=True)
    invoice_number = models.CharField(max_length=250, null=True, blank=True)
    invoice_example = models.SmallIntegerField(choices=INVOICE_EXP)
    invoice_method = models.SmallIntegerField(choices=INVOICE_METHOD, default=3)
    invoice_status = models.SmallIntegerField(choices=INVOICE_STATUS, default=0)
    buyer_information = models.TextField(blank=True)
    is_created_einvoice = models.BooleanField(default=False)
    sum_pretax_value = models.FloatField(default=0)
    sum_discount_value = models.FloatField(default=0)
    sum_tax_value = models.FloatField(default=0)
    sum_after_tax_value = models.FloatField(default=0)
    cash_inflow_done = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return '1d7291dd-1e59-4917-83a3-1cc07cfc4638'

    @classmethod
    def push_final_acceptance_invoice(cls, instance):
        sale_order_id = None
        lease_order_id = None
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
                lease_order_id=lease_order_id,
                employee_created_id=instance.employee_created_id,
                employee_inherit_id=instance.employee_inherit_id,
                opportunity_id=opportunity_id,
                list_data_indicator=list_data_indicator,
            )
        return True

    @classmethod
    def update_order_delivery_is_done_ar_invoice(cls, instance):
        for item in instance.ar_invoice_items.all():
            if item.delivery_item_mapped:
                item.delivery_item_mapped.ar_value_done += item.product_payment_value
                item.delivery_item_mapped.save(update_fields=['ar_value_done'])
        for item_mapped in instance.ar_invoice_deliveries.all():
            count = 0
            all_delivery_item = item_mapped.delivery_mapped.delivery_product_delivery_sub.all()
            for prd in all_delivery_item:
                if prd.ar_value_done == prd.product_cost * prd.picked_quantity:
                    count += 1
            if count == all_delivery_item.count():
                item_mapped.delivery_mapped.is_done_ar_invoice = True
                item_mapped.delivery_mapped.save(update_fields=['is_done_ar_invoice'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    self.update_order_delivery_is_done_ar_invoice(self)
                    JEDocDataLogHandler.push_data_to_je_doc_data(self)
                    # ReconForARInvoiceHandler.auto_create_recon_doc(self)

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
    order = models.IntegerField(default=0)
    delivery_item_mapped = models.ForeignKey('delivery.OrderDeliveryProduct', null=True, on_delete=models.SET_NULL)

    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_data = models.JSONField(default=dict)
    product_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.SET_NULL, null=True)
    product_uom_data = models.JSONField(default=dict)
    product_quantity = models.FloatField(default=1)
    product_unit_price = models.FloatField(default=0)

    product_subtotal = models.FloatField(default=0)

    product_payment_percent = models.FloatField(default=100, null=True)
    product_payment_value = models.FloatField(default=0)

    product_discount_percent = models.FloatField(default=0, null=True)
    product_discount_value = models.FloatField(default=0)

    product_tax = models.ForeignKey('saledata.Tax', on_delete=models.SET_NULL, null=True)
    product_tax_data = models.JSONField(default=dict)
    product_tax_value = models.FloatField(default=0)

    product_subtotal_final = models.FloatField(default=0)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = 'AR Invoice Item'
        verbose_name_plural = 'AR Invoice Items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ARInvoiceDelivery(SimpleAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_deliveries')
    delivery_mapped = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE)
    delivery_mapped_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'AR Invoice Delivery'
        verbose_name_plural = 'AR Invoice Deliveries'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ARInvoiceAttachmentFile(M2MFilesAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_attachments')

    @classmethod
    def get_doc_field_name(cls):
        return 'ar_invoice'

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
