from apps.core.diagram.models import DiagramSuffix


class POHandler:
    @classmethod
    def push_diagram(cls, instance):
        data_push = {}
        list_reference = []
        for po_pr_product in instance.purchase_order_request_product_order.all():
            if po_pr_product.purchase_request_product and po_pr_product.purchase_order_product:
                if po_pr_product.purchase_request_product.purchase_request:
                    if po_pr_product.purchase_request_product.purchase_request.sale_order:
                        so_id = po_pr_product.purchase_request_product.purchase_request.sale_order_id
                        quantity = po_pr_product.quantity_order
                        total = po_pr_product.purchase_order_product.product_unit_price * quantity
                        if str(so_id) not in data_push:
                            data_push.update({
                                str(po_pr_product.purchase_request_product.purchase_request.sale_order_id): {
                                    'quantity': quantity,
                                    'total': total,
                                }
                            })
                        else:
                            data_push[str(so_id)]['quantity'] += quantity
                            data_push[str(so_id)]['total'] += total
        for purchase_request in instance.purchase_requests.all():
            list_reference.append(purchase_request.code)
        for purchase_request in instance.purchase_requests.all():
            if purchase_request.sale_order:
                list_reference.reverse()
                reference = ", ".join(list_reference)
                DiagramSuffix.push_diagram_suffix(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    app_code_main=purchase_request.sale_order.__class__.get_model_code(),
                    doc_id_main=purchase_request.sale_order.id,
                    app_code=instance.__class__.get_model_code(),
                    doc_id=instance.id,
                    doc_data={
                        'id': str(instance.id),
                        'title': instance.title,
                        'code': instance.code,
                        'system_status': instance.system_status,
                        'date_created': str(instance.date_created),
                        # custom
                        'quantity': data_push.get(str(purchase_request.sale_order_id), {}).get('quantity', 0),
                        'total': data_push.get(str(purchase_request.sale_order_id), {}).get('total', 0),
                        'reference': reference,
                    }
                )
        return True
