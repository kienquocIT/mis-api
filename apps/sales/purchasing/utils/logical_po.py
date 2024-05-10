from apps.core.diagram.models import DiagramSuffix


class POHandler:
    @classmethod
    def push_diagram(cls, instance):
        for purchase_request in instance.purchase_requests.all():
            if purchase_request.sale_order:
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
                    }
                )
        return True
