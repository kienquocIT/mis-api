from apps.sales.paymentplan.models import PaymentPlan


class CashOutFlowFinishHandler:

    @classmethod
    def push_to_payment_plan(cls, instance):
        for payment in instance.cash_outflow_item_cash_outflow.all():
            if payment.has_ap_invoice is True:
                for payment_item in payment.cash_outflow_item_detail_cash_outflow_item.all():
                    PaymentPlan.push_from_cash_out_flow(
                        purchase_order_id=payment.purchase_order_id,
                        payment_stage_id=payment_item.po_pm_stage_id,
                        ap_invoice_id=payment.ap_invoice_id,
                        ap_invoice_data={
                            'id': str(payment.ap_invoice_id),
                            'title': payment.ap_invoice.title,
                            'code': payment.ap_invoice.code,
                        } if payment.ap_invoice else {},
                        invoice_actual_date=payment.ap_invoice.invoice_date if payment.ap_invoice else None,
                        value_balance=payment_item.balance_value,
                        value_pay=payment_item.payment_value,
                    )
            if payment.has_ap_invoice is False:
                PaymentPlan.push_from_cash_out_flow(
                    purchase_order_id=payment.purchase_order_id,
                    payment_stage_id=payment.purchase_order_stage_id,
                    ap_invoice_id=payment.ap_invoice_id,
                    ap_invoice_data={
                        'id': str(payment.ap_invoice_id),
                        'title': payment.ap_invoice.title,
                        'code': payment.ap_invoice.code,
                    } if payment.ap_invoice else {},
                    invoice_actual_date=payment.ap_invoice.invoice_date if payment.ap_invoice else None,
                    value_balance=payment.sum_balance_value,
                    value_pay=payment.sum_payment_value,
                )
        return True
