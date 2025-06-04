from apps.sales.paymentplan.models import PaymentPlan


class CashInFlowFinishHandler:

    @classmethod
    def push_to_payment_plan(cls, instance):
        for payment in instance.cash_inflow_item_cash_inflow.all():
            if payment.has_ar_invoice is True:
                for payment_item in payment.cash_inflow_item_detail_cash_inflow_item.all():
                    PaymentPlan.push_from_cash_in_flow(
                        sale_order_id=payment.sale_order_id,
                        payment_stage_id=payment_item.so_pm_stage_id,
                        ar_invoice_id=payment.ar_invoice_id,
                        ar_invoice_data={
                            'id': str(payment.ar_invoice_id),
                            'title': payment.ar_invoice.title,
                            'code': payment.ar_invoice.code,
                        } if payment.ar_invoice else {},
                        invoice_actual_date=payment.ar_invoice.invoice_date if payment.ar_invoice else None,
                        value_balance=payment_item.balance_value,
                        value_pay=payment_item.payment_value,
                    )
            if payment.has_ar_invoice is False:
                PaymentPlan.push_from_cash_in_flow(
                    sale_order_id=payment.sale_order_id,
                    payment_stage_id=payment.sale_order_stage_id,
                    ar_invoice_id=payment.ar_invoice_id,
                    ar_invoice_data={
                        'id': str(payment.ar_invoice_id),
                        'title': payment.ar_invoice.title,
                        'code': payment.ar_invoice.code,
                    } if payment.ar_invoice else {},
                    invoice_actual_date=payment.ar_invoice.invoice_date if payment.ar_invoice else None,
                    value_balance=payment.sum_balance_value,
                    value_pay=payment.sum_payment_value,
                )
        return True
