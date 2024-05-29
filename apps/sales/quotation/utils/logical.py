from apps.core.diagram.models import DiagramPrefix


class QuotationHandler:
    @classmethod
    def push_diagram(cls, instance):
        for sale_order in instance.sale_order_quotation.all():
            quantity = 0
            for quo_product in instance.quotation_product_quotation.all():
                quantity += quo_product.product_quantity
            DiagramPrefix.push_diagram_prefix(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                app_code_main=sale_order.__class__.get_model_code(),
                doc_id_main=sale_order.id,
                app_code=instance.__class__.get_model_code(),
                doc_id=instance.id,
                doc_data={
                    'id': str(instance.id),
                    'title': instance.title,
                    'code': instance.code,
                    'system_status': instance.system_status,
                    'date_created': str(instance.date_created),
                    # custom
                    'quantity': quantity,
                    'total': instance.total_product_pretax_amount,
                }
            )
        return True
