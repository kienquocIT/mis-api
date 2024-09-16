from rest_framework import serializers

from apps.core.base.models import Application
from apps.sales.contract.models import ContractDocument, ContractAttachment
from apps.shared.translations.base import AttachmentMsg


class ContractCommonCreate:

    @classmethod
    def handle_attach_file(cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="58385bcf-f06c-474e-a372-cadc8ea30ecc").first()
            if relate_app:
                state = ContractAttachment.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True

    @classmethod
    def create_document(cls, validated_data, instance):
        ContractDocument.objects.bulk_create([
            ContractDocument(
                contract_approval=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **document
            ) for document in validated_data['document_data']
        ])
        # for document in documents:
        #     document.contract_doc_attachment_doc.all().delete()
        #     ContractDocumentAttachment.objects.bulk_create([ContractDocumentAttachment(
        #         contract_document=document, attachment_id=attachment_data.get('attachment', {}).get('id', None),
        #         order=attachment_data.get('order', 1),
        #     ) for attachment_data in document.attachment_data])
        return True

    @classmethod
    def create_sub_models(cls, validated_data, instance):
        if 'document_data' in validated_data:
            cls.create_document(validated_data=validated_data, instance=instance)
        return True
