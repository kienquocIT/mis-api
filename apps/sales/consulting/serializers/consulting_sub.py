from rest_framework import serializers
from apps.core.base.models import Application
from apps.sales.consulting.models import ConsultingDocument, ConsultingAttachment, ConsultingProductCategory
from apps.shared.translations.base import AttachmentMsg


class ConsultingCommonCreate:
    @classmethod
    def handle_attach_file( cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="3a369ba5-82a0-4c4d-a447-3794b67d1d02").first()
            if relate_app:
                state = ConsultingAttachment.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True

    @classmethod
    def create_sub_models( cls, instance, create_data):
        if create_data.get('document_data'):
            cls.create_document(document_data=create_data.get('document_data'), instance=instance,
                                attachment_result=create_data.get('attachment'))
        if create_data.get('product_categories'):
            cls.create_product_categories(product_categories=create_data.get('product_categories'), instance=instance)
        return True

    @classmethod
    def create_product_categories(cls, product_categories, instance):
        bulk_data = []
        for item in product_categories:
            bulk_data.append(
                ConsultingProductCategory(
                    consulting=instance,
                    order=item.get('order'),
                    value=item.get('value'),
                    product_category=item.get('product_category'),
                )
            )
        ConsultingProductCategory.objects.filter(consulting=instance).delete()
        ConsultingProductCategory.objects.bulk_create(bulk_data)


    @classmethod
    def create_document( cls,document_data, instance, attachment_result):
        bulk_data = []
        for item in document_data:
            bulk_data.append(
                ConsultingDocument(
                    consulting=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **item
                )
            )
        ConsultingDocument.objects.filter(consulting=instance).delete()
        cls.handle_attach_file(instance=instance, attachment_result=attachment_result)
        consulting_doc_instance_list = ConsultingDocument.objects.bulk_create(bulk_data)
        for consulting_doc_instance in consulting_doc_instance_list:
            for item in consulting_doc_instance.attachment_data:
                consulting_attach_instance = ConsultingAttachment.objects.filter_current(
                    attachment_id=item.get('attachment').get('id') if item.get('attachment') else None,
                    consulting=instance
                ).first()
                if consulting_attach_instance:
                    consulting_attach_instance.document = consulting_doc_instance
                    consulting_attach_instance.save(update_fields=['document'])
