from django.db import models
from apps.accounting.accountingsettings.utils.je_doc_data_log_handler import JEDocDataLogHandler
from apps.core.company.models import CompanyFunctionNumber
from apps.sales.financialcashflow.utils.logical_finish_cif import CashInFlowFinishHandler
# from apps.sales.reconciliation.utils.autocreate_recon_for_cash_inflow import ReconForCIFHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel


__all__ = ['CashInflow', 'CashInflowItem', 'CashInflowItemDetail']


class CashInflow(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="cash_inflow_customer",
        null=True
    )
    customer_data = models.JSONField(default=dict)  # {'id', 'code', 'name', 'tax_code'}
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    purchase_advance_value = models.FloatField(default=0)  # tiền tạm ứng mua hàng (không theo SO)
    no_ar_invoice_value = models.FloatField(default=0)  # tổng tiền nhận của khách hàng không hóa đơn (theo SO)
    has_ar_invoice_value = models.FloatField(default=0)  # tổng tiền nhận của khách hàng có hóa đơn (theo SO)
    total_value = models.FloatField(default=0)
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

    def update_ar_invoice_cash_inflow_done(self):
        """
        Cập nhập lại field 'cash_inflow_done' = True trong ar_invoice để biết Hóa đơn đã làm xong phiếu thu
        """
        for item in self.cash_inflow_item_cash_inflow.all():
            ar_invoice_obj = item.ar_invoice
            if ar_invoice_obj:
                if sum(
                        CashInflowItem.objects.filter(
                            ar_invoice=ar_invoice_obj
                        ).values_list('sum_payment_value', flat=True)
                ) == ar_invoice_obj.sum_after_tax_value:
                    ar_invoice_obj.cash_inflow_done = True
                    ar_invoice_obj.save(update_fields=['cash_inflow_done'])
        return True

    def update_so_stage_cash_inflow_done(self):
        """
        Cập nhập lại field 'cash_inflow_done' = True trong so stage để biết Tạm ứng đã làm xong phiếu thu
        """
        for item in self.cash_inflow_item_cash_inflow.all():
            sale_order_stage_obj = item.sale_order_stage
            if sale_order_stage_obj:
                if sum(
                        CashInflowItem.objects.filter(
                            sale_order_stage=sale_order_stage_obj
                        ).values_list('sum_payment_value', flat=True)
                ) == sale_order_stage_obj.value_total:
                    sale_order_stage_obj.cash_inflow_done = True
                    sale_order_stage_obj.save(update_fields=['cash_inflow_done'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
                    self.update_ar_invoice_cash_inflow_done()
                    self.update_so_stage_cash_inflow_done()
                    CashInFlowFinishHandler.push_to_payment_plan(instance=self)  # payment plan
                    JEDocDataLogHandler.push_data_to_je_doc_data(self)
                    # ReconForCIFHandler.auto_create_recon_doc(self)
        super().save(*args, **kwargs)


class CashInflowItem(SimpleAbstractModel):
    cash_inflow = models.ForeignKey(
        CashInflow,
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_cash_inflow",
    )
    cash_inflow_data = models.JSONField(default=dict)  # # {'id', 'code', title'}
    has_ar_invoice = models.BooleanField(default=False)
    ar_invoice = models.ForeignKey(
        'arinvoice.ARInvoice',
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_ar_invoice",
        null=True
    )
    ar_invoice_data = models.JSONField(default=dict)
    # ar_invoice_data = {
    #     'id', 'code', title',
    #     'type_doc': str,
    #     'document_date': str,
    #     'sum_total_value': number
    # }

    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_sale_order",
    )
    sale_order_data = models.JSONField(default=dict)  # {'id', 'code', title'}
    sale_order_stage = models.ForeignKey(
        'saleorder.SaleOrderPaymentStage',
        on_delete=models.CASCADE,
        related_name="cash_inflow_item_so_stage",
        null=True
    )
    sale_order_stage_data = models.JSONField(default=dict)
    # sale_order_stage_data = {
    #     'id': uuid,
    #     'remark': str,
    #     'term_data': dict,
    #     'date': str,
    #     'date_type': str,
    #     'payment_ratio': str,
    #     'value_before_tax': number,
    #     'invoice': number,
    #     'invoice_data': dict,
    #     'value_total': number,
    #     'due_date': str,
    #     'is_ar_invoice': bool,
    #     'order': number,
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
    """
    Map với các Stage thanh toán (trong Sale Order) cho trường hợp thu tiền hóa đơn
    """
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
    #     'invoice': number,
    #     'invoice_data': dict,
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
