from rest_framework import serializers

# from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.contract.models import Contract, ContractDocument
from apps.sales.contract.serializers.contract_sub import ContractCommonCreate
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel


# SUB
class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractDocument
        fields = (
            'id',
            'title',
            'remark',
            'attachment_data',
            'order',
        )


# CONTRACT BEGIN
class ContractListSerializer(AbstractListSerializerModel):

    class Meta:
        model = Contract
        fields = (
            'id',
            'title',
            'code',
        )


class ContractDetailSerializer(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
        )


class ContractCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField()
    document_data = DocumentCreateSerializer(many=True, required=False)

    class Meta:
        model = Contract
        fields = (
            'title',
            'document_data',
        )

    # @decorator_run_workflow
    def create(self, validated_data):
        contract = Contract.objects.create(**validated_data)
        ContractCommonCreate.create_sub_models(
            validated_data=validated_data,
            instance=contract,
        )
        return contract


class ContractUpdateSerializer(AbstractCreateSerializerModel):
    document_data = DocumentCreateSerializer(many=True, required=False)

    class Meta:
        model = Contract
        fields = (
            'title',
            'document_data',
        )

    # @decorator_run_workflow
    def update(self, instance, validated_data):
        # update quotation
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
