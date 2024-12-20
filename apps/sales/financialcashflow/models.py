from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, SimpleAbstractModel, BastionFieldAbstractModel
from apps.core.company.models import CompanyFunctionNumber

__all__ = ['CashInflow', 'CashInflowARInvoice']


class CashInflow(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="cash_inflow_customer",
        null=True
    )
    customer_data = models.JSONField(default=dict)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    purchase_advance_value = models.FloatField(default=0)
    total_value = models.FloatField(default=0)
    cash_value = models.FloatField(default=0)
    bank_value = models.FloatField(default=0)
    # sau này sẽ thay thế bằng 2 obj tài khoản kế toán, hiện tại chỉ lưu text
    accounting_cash_account = models.CharField(default='1111', max_length=50)
    accounting_bank_account = models.FloatField(default='1121', max_length=50)
    company_bank_account = models.ForeignKey(
        'company.CompanyBankAccount',
        on_delete=models.CASCADE,
        related_name="cash_inflow_company_bank_account",
    )
    company_bank_account_data = models.JSONField(default=dict)

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
        # hit DB
        super().save(*args, **kwargs)


class CashInflowARInvoice(DataAbstractModel):
    cash_inflow = models.ForeignKey(
        CashInflow,
        on_delete=models.CASCADE,
        related_name="cash_inflow_ar_invoice_cash_inflow",
    )
    cash_inflow_data = models.JSONField(default=dict)
    ar_invoice = models.ForeignKey(
        'arinvoice.ARInvoice',
        on_delete=models.CASCADE,
        related_name="cash_inflow_ar_invoice_ar_invoice",
    )
    ar_invoice_data = models.JSONField(default=dict)
    total_value = models.FloatField(default=0)
    balance_value = models.FloatField(default=0)
    payment_value = models.FloatField(default=0)
    discount_payment = models.FloatField(default=0)
