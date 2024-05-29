from apps.core.diagram.models import DiagramDocument, DiagramPrefix


class SOHandler:
    @classmethod
    def push_diagram(cls, instance):
        quantity = 0
        list_reference = []
        if instance.quotation:
            list_reference.append(instance.quotation.code)
        for so_product in instance.sale_order_product_sale_order.all():
            quantity += so_product.product_quantity
        list_reference.reverse()
        reference = ", ".join(list_reference)
        DiagramDocument.push_diagram_document(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
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
                'reference': reference,
            }
        )
        if instance.quotation:
            quantity = 0
            for quo_product in instance.quotation.quotation_product_quotation.all():
                quantity += quo_product.product_quantity
            DiagramPrefix.push_diagram_prefix(
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                app_code_main=instance.__class__.get_model_code(),
                doc_id_main=instance.id,
                app_code=instance.quotation.__class__.get_model_code(),
                doc_id=instance.quotation.id,
                doc_data={
                    'id': str(instance.quotation.id),
                    'title': instance.quotation.title,
                    'code': instance.quotation.code,
                    'system_status': instance.quotation.system_status,
                    'date_created': str(instance.quotation.date_created),
                    # custom
                    'quantity': quantity,
                    'total': instance.quotation.total_product_pretax_amount,
                }
            )
        return True
