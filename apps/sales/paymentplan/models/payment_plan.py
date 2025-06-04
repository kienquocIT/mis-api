from django.db import models

from apps.shared import DataAbstractModel


# PAYMENT PLAN
class PaymentPlan(DataAbstractModel):
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name='payment_plan_sale_order',
        null=True,
    )
    sale_order_data = models.JSONField(default=dict, help_text='data json of sale_order')
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.CASCADE,
        related_name='payment_plan_purchase_order',
        null=True
    )
    purchase_order_data = models.JSONField(default=dict, help_text='data json of purchase_order')
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="payment_plan_customer",
        null=True,
    )
    customer_data = models.JSONField(default=dict, help_text='data json of customer')
    supplier = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="supplier",
        related_name="payment_plan_supplier",
        null=True,
    )
    supplier_data = models.JSONField(default=dict, help_text='data json of supplier')
    so_payment_stage = models.ForeignKey(
        'saleorder.SaleOrderPaymentStage',
        on_delete=models.SET_NULL,
        verbose_name="payment stage",
        related_name="payment_plan_so_payment_stage",
        null=True
    )
    so_payment_stage_data = models.JSONField(default=dict, help_text='data json of so_payment_stage')
    ar_invoice = models.ForeignKey(
        'arinvoice.ARInvoice',
        on_delete=models.CASCADE,
        verbose_name="ar invoice",
        related_name="payment_plan_ar_invoice",
        null=True
    )
    ar_invoice_data = models.JSONField(default=dict, help_text='data json of ar_invoice')
    po_payment_stage = models.ForeignKey(
        'purchasing.PurchaseOrderPaymentStage',
        on_delete=models.SET_NULL,
        verbose_name="payment stage",
        related_name="payment_plan_po_payment_stage",
        null=True
    )
    po_payment_stage_data = models.JSONField(default=dict, help_text='data json of po_payment_stage')
    ap_invoice = models.ForeignKey(
        'apinvoice.APInvoice',
        on_delete=models.CASCADE,
        verbose_name="ap invoice",
        related_name="payment_plan_ap_invoice",
        null=True
    )
    ap_invoice_data = models.JSONField(default=dict, help_text='data json of ap_invoice')
    value_balance = models.FloatField(default=0)
    value_pay = models.FloatField(default=0)
    invoice_planned_date = models.DateTimeField(null=True)
    invoice_actual_date = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    group_inherit = models.ForeignKey(
        'hr.Group',
        null=True,
        on_delete=models.SET_NULL,
        related_name='payment_plan_group_inherit',
    )

    @classmethod
    def push_from_so_po(cls, bulk_data):
        cls.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def push_from_invoice(cls, sale_order=None, purchase_order=None, invoice_actual_date=None):
        if sale_order:
            for obj in cls.objects.filter(sale_order=sale_order):
                if not obj.invoice_actual_date:
                    obj.invoice_actual_date = invoice_actual_date
                    obj.save(update_fields=['invoice_actual_date'])
                    break
        if purchase_order:
            for obj in cls.objects.filter(purchase_order=purchase_order):
                if not obj.invoice_actual_date:
                    obj.invoice_actual_date = invoice_actual_date
                    obj.save(update_fields=['invoice_actual_date'])
                    break
        return True

    @classmethod
    def push_from_cash_in_flow(
            cls,
            sale_order_id=None,
            payment_stage_id=None,
            ar_invoice_id=None,
            ar_invoice_data=None,
            invoice_actual_date=None,
            value_balance=0,
            value_pay=0,
    ):
        if sale_order_id and payment_stage_id:
            plan_obj = cls.objects.filter(sale_order_id=sale_order_id, so_payment_stage_id=payment_stage_id).first()
            if plan_obj:
                plan_obj.ar_invoice_id = ar_invoice_id if ar_invoice_id else None
                plan_obj.ar_invoice_data = ar_invoice_data if ar_invoice_data else {}
                plan_obj.invoice_actual_date = invoice_actual_date
                plan_obj.value_balance = value_balance
                plan_obj.value_pay = value_pay
                plan_obj.save(update_fields=[
                    'ar_invoice_id', 'ar_invoice_data', 'invoice_actual_date', 'value_balance', 'value_pay'
                ])
        return True

    @classmethod
    def push_from_cash_out_flow(
            cls,
            purchase_order_id=None,
            payment_stage_id=None,
            ap_invoice_id=None,
            ap_invoice_data=None,
            invoice_actual_date=None,
            value_balance=0,
            value_pay=0,
    ):
        if purchase_order_id and payment_stage_id:
            if ap_invoice_id:
                plan_obj = cls.objects.filter(
                    purchase_order_id=purchase_order_id, po_payment_stage_id=payment_stage_id
                ).first()
                if plan_obj:
                    plan_obj.ap_invoice_id = ap_invoice_id
                    plan_obj.ap_invoice_data = ap_invoice_data if ap_invoice_data else {}
                    plan_obj.invoice_actual_date = invoice_actual_date
                    plan_obj.value_balance = value_balance
                    plan_obj.value_pay = value_pay
                    plan_obj.save(update_fields=[
                        'ap_invoice_id', 'ap_invoice_data', 'invoice_actual_date', 'value_balance', 'value_pay'
                    ])
        return True

    class Meta:
        verbose_name = 'Payment Plan'
        verbose_name_plural = 'Payment Plans'
        ordering = ('due_date',)
        default_permissions = ()
        permissions = ()
