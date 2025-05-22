from apps.sales.paymentplan.models import PaymentPlan


class ARInvoiceFinishHandler:

    @classmethod
    def push_to_payment_plan(cls, instance):
        PaymentPlan.push_from_invoice(sale_order=instance.sale_order_mapped, invoice_actual_date=instance.invoice_date)
        return True
