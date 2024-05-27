from apps.sales.report.models import ReportCashflow


class POFinishHandler:
    @classmethod
    def update_remain_and_status_purchase_request(cls, instance):
        # update quantity remain on purchase request product
        for po_request in instance.purchase_order_request_product_order.filter(is_stock=False):
            po_request.purchase_request_product.remain_for_purchase_order -= po_request.quantity_order
            po_request.purchase_request_product.save(update_fields=['remain_for_purchase_order'])
        return True

    @classmethod
    def update_is_all_ordered_purchase_request(cls, instance):
        for pr_obj in instance.purchase_requests.all():
            pr_product = pr_obj.purchase_request.all()
            pr_product_done = pr_obj.purchase_request.filter(remain_for_purchase_order=0)
            if pr_product.count() == pr_product_done.count():  # All PR products ordered
                pr_obj.purchase_status = 2
                pr_obj.is_all_ordered = True
                pr_obj.save(update_fields=['purchase_status', 'is_all_ordered'])
            else:  # Partial PR products ordered
                pr_obj.purchase_status = 1
                pr_obj.save(update_fields=['purchase_status'])
        return True

    @classmethod
    def push_product_info(cls, instance):
        for product_purchase in instance.purchase_order_product_order.all():
            uom_transaction = product_purchase.uom_order_actual
            if product_purchase.uom_order_request:
                uom_transaction = product_purchase.uom_order_request
            final_ratio = cls.get_final_uom(
                product_obj=product_purchase.product, uom_transaction=uom_transaction
            )
            product_quantity_order_request_final = product_purchase.product_quantity_order_actual * final_ratio
            if instance.purchase_requests.exists():
                product_quantity_order_request_final = product_purchase.product_quantity_order_request * final_ratio
            stock_final = product_purchase.stock * final_ratio
            product_purchase.product.save(**{
                'update_transaction_info': True,
                'quantity_purchase': product_quantity_order_request_final + stock_final,
                'update_fields': ['wait_receipt_amount', 'available_amount']
            })
        return True

    @classmethod
    def push_to_report_cashflow(cls, instance):
        if instance.tenant and instance.company and instance.employee_inherit:
            # payment
            bulk_data = [ReportCashflow(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                sale_order_id=None,
                purchase_order_id=instance.id,
                cashflow_type=3,
                employee_inherit_id=instance.employee_inherit_id,
                group_inherit_id=instance.employee_inherit.group_id,
                due_date=payment_stage.due_date,
                value_estimate_cost=payment_stage.value_before_tax,
            ) for payment_stage in instance.purchase_order_payment_stage_po.all()]
            ReportCashflow.push_from_so_po(bulk_data)
        return True

    @classmethod
    def get_final_uom(cls, product_obj, uom_transaction):
        if product_obj.general_uom_group:
            uom_base = product_obj.general_uom_group.uom_reference
            if uom_base and uom_transaction:
                return uom_transaction.ratio / uom_base.ratio
        return 1
