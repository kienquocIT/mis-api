from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import SimpleAbstractModel, DataAbstractModel, AutoDocumentAbstractModel


__all__ = [
    'Reconciliation',
    'ReconciliationItem',
]


RECON_TYPE = [
    (0, _('Reconciliation of Customer')),
    (1, _('Reconciliation of Supplier')),
    (2, _('Reconciliation of Employee')),
]


class Reconciliation(DataAbstractModel, AutoDocumentAbstractModel):
    recon_type = models.SmallIntegerField(choices=RECON_TYPE, default=0)
    business_partner = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="recon_business_partner",
        null=True
    )
    business_partner_data = models.JSONField(default=dict)
    # business_partner_data = {
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
        self.add_auto_generate_code_to_instance(self, 'RECON[n4]', False, kwargs)
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
    debit_app_code = models.CharField(
        max_length=100,
        verbose_name='Code of debit application',
        help_text='{app_label}.{model}',
        null = True
    )
    debit_doc_id = models.UUIDField(verbose_name='Debit document id', null=True)
    debit_doc_data = models.JSONField(default=dict)
    # debit_doc_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str,
    #     'document_date': str,
    #     'posting_date': str,
    # }
    debit_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='recon_item_debit_account',
        null=True
    )
    debit_account_data = models.JSONField(default=dict)
    credit_app_code = models.CharField(
        max_length=100,
        verbose_name='Code of credit application',
        help_text='{app_label}.{model}',
        null=True
    )
    credit_doc_id = models.UUIDField(verbose_name='Credit document id', null=True)
    credit_doc_data = models.JSONField(default=dict)
    # credit_doc_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str,
    #     'document_date': str,
    #     'posting_date': str,
    # }
    credit_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='recon_item_credit_account',
        null=True
    )
    credit_account_data = models.JSONField(default=dict)
    recon_total = models.FloatField(default=0)
    recon_balance = models.FloatField(default=0)
    recon_amount = models.FloatField(default=0)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Reconciliation item'
        verbose_name_plural = 'Reconciliation items'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
