from apps.sales.contract.models import ContractDocument


class ContractCommonCreate:

    @classmethod
    def create_document(cls, instance, validated_data):
        ContractDocument.objects.bulk_create([
            ContractDocument(
                contract=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **document
            ) for document in validated_data['document_data']
        ])
        return True

    @classmethod
    def delete_old_document(cls, instance):
        instance.contract_doc_contract.all().delete()
        return True

    @classmethod
    def create_sub_models(cls, validated_data, instance, is_update=False):
        if 'document_data' in validated_data:
            if is_update is True:
                cls.delete_old_document(instance=instance)
            cls.create_document(validated_data=validated_data, instance=instance)
        return True
