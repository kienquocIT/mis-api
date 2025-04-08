from django.db import models
from apps.accounting.journalentry.utils.log_for_cash_inflow import JEForCIFHandler
from apps.sales.reconciliation.utils.autocreate_recon_for_cash_inflow import ReconForCIFHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel


__all__ = ['CashOutflow', 'CashOutflowItem', 'CashOutflowItemDetail']


class CashOutflow(DataAbstractModel):
    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="cash_outflow_supplier",
        null=True
    )
    supplier_data = models.JSONField(default=dict)
    # supplier_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="cash_outflow_customer",
        null=True
    )
    customer_data = models.JSONField(default=dict)
    # customer_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="cash_outflow_employee",
        null=True
    )
    employee_data = models.JSONField(default=dict)
    # employee_data = {
    #     'id': uuid,
    #     'code': str,
    #     'full_name': str,
    #     'group': {
    #         'id': uuid,
    #         'code': str,
    #         'title': str
    #      }
    # }
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    advance_for_supplier_value = models.FloatField(default=0)  # tiền tạm ứng cho NCC (không theo PO)
    no_ap_invoice_value = models.FloatField(default=0)  # tổng tiền nhận của NCC không hóa đơn (theo PO)
    has_ap_invoice_value = models.FloatField(default=0)  # tổng tiền nhận của NCC có hóa đơn (theo PO)
    total_value = models.FloatField(
        default=0,
        help_text="total_value = advance_for_supplier_value + no_ap_invoice_value + has_ap_invoice_value"
    )
    # payment method
    cash_value = models.FloatField(default=0)
    bank_value = models.FloatField(default=0)
    company_bank_account = models.ForeignKey(
        'saledata.BankAccount',
        on_delete=models.CASCADE,
        related_name="cash_outflow_company_bank_account",
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
        verbose_name = 'Cash Outflow'
        verbose_name_plural = 'Cash Outflow'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def update_ap_invoice_cash_outflow_done(self):
        """
        Cập nhập lại field 'cash_outflow_done' = True trong ap_invoice để biết Hóa đơn đã làm xong phiếu chi
        """
        for item in self.cash_outflow_item_cash_outflow.all():
            ap_invoice_obj = item.ap_invoice
            if ap_invoice_obj:
                if sum(
                        CashOutflowItem.objects.filter(
                            ar_invoice=ap_invoice_obj
                        ).values_list('sum_payment_value', flat=True)
                ) == ap_invoice_obj.sum_after_tax_value:
                    ap_invoice_obj.cash_outflow_done = True
                    ap_invoice_obj.save(update_fields=['cash_outflow_done'])
        return True

    def update_po_stage_cash_outflow_done(self):
        """
        Cập nhập lại field 'cash_outflow_done' = True trong po stage để biết Tạm ứng đã làm xong phiếu chi
        """
        for item in self.cash_outflow_item_cash_outflow.all():
            purchase_order_stage_obj = item.purchase_order_stage
            if purchase_order_stage_obj:
                if sum(
                        CashOutflowItem.objects.filter(
                            purchase_order_stage=purchase_order_stage_obj
                        ).values_list('sum_payment_value', flat=True)
                ) == purchase_order_stage_obj.value_total:
                    purchase_order_stage_obj.cash_outflow_done = True
                    purchase_order_stage_obj.save(update_fields=['cash_outflow_done'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'COF[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                JEForCIFHandler.push_to_journal_entry(self)
                ReconForCIFHandler.auto_create_recon_doc(self)
                self.update_ap_invoice_cash_outflow_done()
                self.update_po_stage_cash_outflow_done()
        super().save(*args, **kwargs)


class CashOutflowItem(SimpleAbstractModel):
    cash_outflow = models.ForeignKey(
        CashOutflow,
        on_delete=models.CASCADE,
        related_name="cash_outflow_item_cash_outflow",
    )
    cash_outflow_data = models.JSONField(default=dict)
    # cash_outflow_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    has_ap_invoice = models.BooleanField(default=False)
    ap_invoice = models.ForeignKey(
        'apinvoice.APInvoice',
        on_delete=models.CASCADE,
        related_name="cash_outflow_item_ap_invoice",
        null=True
    )
    ap_invoice_data = models.JSONField(default=dict)
    # ap_invoice_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str,
    #     'type_doc': str,
    #     'document_date': str,
    #     'sum_total_value': number
    # }
    purchase_order_stage = models.ForeignKey(
        'purchasing.PurchaseOrderPaymentStage',
        on_delete=models.CASCADE,
        related_name="cash_outflow_item_po_stage",
        null=True
    )
    purchase_order_stage_data = models.JSONField(default=dict)
    # purchase_order_stage_data = {
    #     'id': uuid,
    #     'remark': str,
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
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.CASCADE,
        related_name="cash_outflow_item_purchase_order",
    )
    purchase_order_data = models.JSONField(default=dict)
    # purchase_order_data = {
    #     'id': uuid,
    #     'code': str,
    #     'title': str
    # }
    sum_balance_value = models.FloatField(default=0)
    sum_payment_value = models.FloatField(default=0)
    discount_payment = models.FloatField(default=0, help_text='%')
    discount_value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Cash Outflow Item'
        verbose_name_plural = 'Cash Outflow Items'
        ordering = ()
        default_permissions = ()
        permissions = ()


class CashOutflowItemDetail(SimpleAbstractModel):
    """
    Map với các Stage thanh toán (trong Sale Order) cho trường hợp thu tiền hóa đơn
    """
    cash_outflow_item = models.ForeignKey(
        CashOutflowItem,
        on_delete=models.CASCADE,
        related_name="cash_outflow_item_detail_cash_outflow_item",
    )
    po_pm_stage = models.ForeignKey(
        'purchasing.PurchaseOrderPaymentStage',
        on_delete=models.CASCADE,
        related_name="cash_outflow_item_detail_po_pm_stage",
    )
    po_pm_stage_data = models.JSONField(default=dict)
    # po_pm_stage_data = {
    #     'id': uuid,
    #     'remark': str,
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
        verbose_name = 'Cash Outflow Item Details'
        verbose_name_plural = 'Cash Outflow Items Detail'
        ordering = ()
        default_permissions = ()
        permissions = ()
