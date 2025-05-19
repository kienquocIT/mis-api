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
    po_payment_stage = models.ForeignKey(
        'purchasing.PurchaseOrderPaymentStage',
        on_delete=models.SET_NULL,
        verbose_name="payment stage",
        related_name="payment_plan_po_payment_stage",
        null=True
    )
    po_payment_stage_data = models.JSONField(default=dict, help_text='data json of po_payment_stage')
    value_pay = models.FloatField(default=0)
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

    class Meta:
        verbose_name = 'Payment Plan'
        verbose_name_plural = 'Payment Plans'
        ordering = ('-due_date',)
        default_permissions = ()
        permissions = ()
