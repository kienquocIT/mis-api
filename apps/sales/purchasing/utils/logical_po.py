from apps.core.diagram.models import DiagramSuffix


class POHandler:
    @classmethod
    def push_diagram(cls, instance):
        for pr in instance.purchase_requests.all():
            if pr.sale_order:
                DiagramSuffix.push_diagram_suffix(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    app_code_main=pr.sale_order._meta.label_lower,
                    doc_id_main=pr.sale_order.id,
                    app_code=instance._meta.label_lower,
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
