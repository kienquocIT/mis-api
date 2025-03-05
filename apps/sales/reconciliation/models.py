from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import SimpleAbstractModel, DataAbstractModel, AccountingAbstractModel


__all__ = [
    'Reconciliation',
    'ReconciliationItem',
]


RECON_TYPE = [
    (0, _('Reconciliation of Customer')),
    (1, _('Reconciliation of Supplier')),
    (2, _('Reconciliation of Employee')),
]


class Reconciliation(DataAbstractModel, AccountingAbstractModel):
    type = models.SmallIntegerField(choices=RECON_TYPE, default=0)
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="recon_customer",
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

    class Meta:
        verbose_name = 'Reconciliation'
        verbose_name_plural = 'Reconciliations'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        self.add_auto_generate_code_to_instance(self, 'RECON[n4]', False)
        # hit DB
        super().save(*args, **kwargs)


class ReconciliationItem(SimpleAbstractModel):
    recon = models.ForeignKey(Reconciliation, on_delete=models.CASCADE, related_name='recon_items')
    recon_data = models.JSONField(default=dict)
    # recon_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    order = models.IntegerField(default=0)
    ar_invoice = models.ForeignKey(
        'arinvoice.ARInvoice',
        on_delete=models.CASCADE,
        related_name="recon_item_ar_invoice",
        null=True
    )
    ar_invoice_data = models.JSONField(default=dict)
    # ar_invoice_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str,
    #     'type_doc': str,
    #     'document_date': str,
    #     'posting_date': str,
    #     'sum_total_value': number
    # }
    cash_inflow = models.ForeignKey(
        'financialcashflow.CashInflow',
        on_delete=models.CASCADE,
        related_name="recon_item_cash_inflow",
        null=True
    )
    cash_inflow_data = models.JSONField(default=dict)
    # cash_inflow_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str,
    #     'type_doc': str,
    #     'document_date': str,
    #     'posting_date': str,
    #     'sum_total_value': number
    # }
    recon_balance = models.FloatField(default=0)
    recon_amount = models.FloatField(default=0)
    note = models.TextField(blank=True, null=True)
    # sau này sẽ thay thế bằng obj tài khoản kế toán, hiện tại chỉ lưu text
    accounting_account = models.CharField(default='1311', max_length=50)

    class Meta:
        verbose_name = 'Reconciliation item'
        verbose_name_plural = 'Reconciliation items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
