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
    def update_product_wait_receipt_amount(cls, instance):
        for product_purchase in instance.purchase_order_product_order.all():
            uom_product_inventory = product_purchase.product.inventory_uom
            uom_product_po = product_purchase.uom_order_actual
            if product_purchase.uom_order_request:
                uom_product_po = product_purchase.uom_order_request
            final_ratio = 1
            if uom_product_inventory and uom_product_po:
                final_ratio = uom_product_po.ratio / uom_product_inventory.ratio
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
        po_products_json = {}
        if instance.tenant and instance.company and instance.employee_inherit:
            po_products = instance.purchase_order_product_order.all()
            for po_product in po_products:
                if str(po_product.product_id) not in po_products_json:
                    po_products_json.update({str(po_product.product_id): {
                        'po': str(po_product.purchase_order_id),
                        'quantity': po_product.product_quantity_order_actual,
                    }})
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
