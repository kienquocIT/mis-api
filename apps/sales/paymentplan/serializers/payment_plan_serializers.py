from apps.sales.paymentplan.models import PaymentPlan
from apps.shared import AbstractListSerializerModel


# PAYMENT PLAN BEGIN
class PaymentPlanListSerializer(AbstractListSerializerModel):

    class Meta:
        model = PaymentPlan
        fields = (
            'id',
            'sale_order_data',
            'purchase_order_data',
            'customer_data',
            'supplier_data',
            'so_payment_stage_data',
            'po_payment_stage_data',
            'value_pay',
            'invoice_planned_date',
            'invoice_actual_date',
            'due_date',
            'date_approved',
        )
