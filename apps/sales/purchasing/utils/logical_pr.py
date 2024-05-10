from apps.core.diagram.models import DiagramSuffix


class PRHandler:
    @classmethod
    def push_diagram(cls, instance):
        if instance.sale_order:
            quantity = 0
            for pr_product in instance.purchase_request.all():
                quantity += pr_product.quantity
            DiagramSuffix.push_diagram_suffix(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                app_code_main=instance.sale_order.__class__.get_model_code(),
                doc_id_main=instance.sale_order.id,
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
                    'total': instance.pretax_amount,
                }
            )
        return True
