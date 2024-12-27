from django.db import models
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem
from apps.shared import DataAbstractModel

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
    # sau này sẽ thay thế bằng 2 obj tài khoản kế toán, hiện tại chỉ lưu text
    accounting_cash_account = models.CharField(default='1111', max_length=50)
    accounting_bank_account = models.FloatField(default='1121', max_length=50)
    company_bank_account = models.ForeignKey(
        'company.CompanyBankAccount',
        on_delete=models.CASCADE,
        related_name="cash_inflow_company_bank_account",
        null=True
    )
    company_bank_account_data = models.JSONField(default=dict)
    # company_bank_account_data = {
    #     'id': uuid,
    #     'country_id': uuid,
    #     'bank_name': str,
    #     'bank_code': str,
    #     'bank_account_name': str,
    #     'bank_account_number': str,
    #     'bic_swift_code': str,
    #     'is_default': bool
    # }

    class Meta:
        verbose_name = 'Cash Inflow'
        verbose_name_plural = 'Cash Inflow'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def auto_create_recon_doc(cls, cif):
        if cif.has_ar_invoice_value > 0:
            # crete recon for each cash inflow doc
            recon_obj = Reconciliation.objects.create(
                type=0,
                code=f"RECON000{Reconciliation.objects.filter(company_id=cif.company_id).count()}",
                title=f"Reconciliation for {cif.code}",
                customer=cif.customer,
                customer_data=cif.customer_data,
                posting_date=cif.posting_date,
                document_date=cif.document_date,
                system_status=1,
                company_id=cif.company_id,
                tenant_id=cif.tenant_id,
            )
            cif_item = cif.cash_inflow_item_cash_inflow.first()
            if cif_item and cif_item.ar_invoice:
                ReconciliationItem.objects.create(
                    recon=recon_obj,
                    recon_data={
                        'id': str(recon_obj.id),
                        'code': recon_obj.code,
                        'title': recon_obj.title
                    },
                    order=0,
                    ar_invoice=cif_item.ar_invoice,
                    ar_invoice_data=cif_item.ar_invoice_data,
                    recon_balance=cif_item.sum_balance_value,
                    recon_amount=cif.total_value,
                    note='',
                    accounting_account='1311'
                )
                ReconciliationItem.objects.create(
                    recon=recon_obj,
                    recon_data={
                        'id': str(recon_obj.id),
                        'code': recon_obj.code,
                        'title': recon_obj.title
                    },
                    order=1,
                    cash_inflow=cif,
                    cash_inflow_data={
                        'id': str(cif.id),
                        'code': cif.code,
                        'title': cif.title,
                        'type_doc': 'Cash inflow',
                        'document_date': str(cif.document_date),
                        'posting_date': str(cif.posting_date),
                        'sum_total_value': cif.total_value
                    },
                    recon_balance=cif.total_value,
                    recon_amount=cif.total_value,
                    note='',
                    accounting_account='1311'
                )
                return True
            return False

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'CIF[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                self.auto_create_recon_doc(self)
        # hit DB
        super().save(*args, **kwargs)


class CashInflowItem(DataAbstractModel):
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


class CashInflowItemDetail(DataAbstractModel):
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
