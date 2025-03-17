from django.db import models
from apps.accounting.journalentry.utils.log_for_cash_inflow import JEForCIFHandler
from apps.sales.reconciliation.utils.autocreate_recon_for_cash_inflow import ReconForCIFHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel


__all__ = ['CashInflow', 'CashInflowItem', 'CashInflowItemDetail']


class CashInflow(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="cash_inflow_customer",
        null=True
    )
    customer_data = models.JSONField(default=dict)
    # customer_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    purchase_advance_value = models.FloatField(default=0)
    no_ar_invoice_value = models.FloatField(default=0)
    has_ar_invoice_value = models.FloatField(default=0)
    total_value = models.FloatField(
        default=0,
        help_text="total_value = purchase_advance_value + no_ar_invoice_value + has_ar_invoice_value"
    )
    # payment method
    cash_value = models.FloatField(default=0)
    bank_value = models.FloatField(default=0)
    company_bank_account = models.ForeignKey(
        'saledata.BankAccount',
        on_delete=models.CASCADE,
        related_name="cash_inflow_company_bank_account",
        null=True
    )
    company_bank_account_data = models.JSONField(default=dict)
    # company_bank_account_data = {
    #     'id': uuid,
    #     'bank_mapped_data': dict,
    #     'bank_account_owner': str,
    #     'bank_account_number': str,
    #     'brand_name': str,
    #     'brand_address': str,
    # }

    class Meta:
        verbose_name = 'Cash Inflow'
        verbose_name_plural = 'Cash Inflow'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'CIF[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                JEForCIFHandler.push_to_journal_entry(self)
                ReconForCIFHandler.auto_create_recon_doc(self)
        super().save(*args, **kwargs)


class CashInflowItem(SimpleAbstractModel):
    cash_inflow = models.ForeignKey(
        CashInflow,
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_cash_inflow",
    )
    cash_inflow_data = models.JSONField(default=dict)
    # cash_inflow_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    has_ar_invoice = models.BooleanField(default=False)
    ar_invoice = models.ForeignKey(
        'arinvoice.ARInvoice',
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_ar_invoice",
        null=True
    )
    ar_invoice_data = models.JSONField(default=dict)
    # ar_invoice_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str,
    #     'type_doc': str,
    #     'document_date': str,
    #     'sum_total_value': number
    # }
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_sale_order",
    )
    sale_order_data = models.JSONField(default=dict)
    # sale_order_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    sum_balance_value = models.FloatField(default=0)
    sum_payment_value = models.FloatField(default=0)
    discount_payment = models.FloatField(default=0, help_text='%')
    discount_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Cash Inflow Item'
        verbose_name_plural = 'Cash Inflow Items'
        ordering = ()
        default_permissions = ()
        permissions = ()


class CashInflowItemDetail(SimpleAbstractModel):
    cash_inflow_item = models.ForeignKey(
        CashInflowItem,
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_detail_cash_inflow_item",
    )
    so_pm_stage = models.ForeignKey(
        'saleorder.SaleOrderPaymentStage',
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_detail_so_pm_stage",
    )
    so_pm_stage_data = models.JSONField(default=dict)
    # so_pm_stage_data = {
    #     'id': uuid,
    #     'remark': str,
    #     'term_data': dict,
    #     'date': str,
    #     'date_type': str,
    #     'payment_ratio': str,
    #     'value_before_tax': number,
    #     'issue_invoice': number,
    #     'value_after_tax': number,
    #     'value_total': number,
    #     'due_date': str,
    #     'is_ar_invoice': bool,
    #     'order': number,
    # }
    balance_value = models.FloatField(default=0)
    payment_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Cash Inflow Item Details'
        verbose_name_plural = 'Cash Inflow Items Detail'
        ordering = ()
        default_permissions = ()
        permissions = ()
