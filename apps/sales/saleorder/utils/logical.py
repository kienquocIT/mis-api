from apps.core.diagram.models import DiagramDocument, DiagramPrefix


class SOHandler:
    @classmethod
    def push_diagram(cls, instance):
        DiagramDocument.push_diagram_document(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
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
        if instance.quotation:
            DiagramPrefix.push_diagram_prefix(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                app_code_main=instance._meta.label_lower,
                doc_id_main=instance.id,
                app_code=instance.quotation._meta.label_lower,
                doc_id=instance.quotation.id,
                doc_data={
                    'id': str(instance.quotation.id),
                    'title': instance.quotation.title,
                    'code': instance.quotation.code,
                    'system_status': instance.quotation.system_status,
                    'date_created': str(instance.quotation.date_created),
                }
            )
        return True
