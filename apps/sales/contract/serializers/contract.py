from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.contract.models import ContractApproval, ContractDocument, ContractAttachment
from apps.sales.contract.serializers.contract_sub import ContractCommonCreate, ContractValid
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg


# SUB
class DocumentCreateSerializer(serializers.ModelSerializer):
    # attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = ContractDocument
        fields = (
            'title',
            'remark',
            # 'attachment',
            'attachment_data',
            'order',
        )


# CONTRACT BEGIN
class ContractApprovalListSerializer(AbstractListSerializerModel):

    class Meta:
        model = ContractApproval
        fields = (
            'id',
            'title',
            'code',
        )


class ContractApprovalDetailSerializer(AbstractDetailSerializerModel):
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = ContractApproval
        fields = (
            'id',
            'title',
            'code',
            'opportunity_data',
            'employee_inherit_data',
            'document_data',
            'attachment',
            'abstract_content',
            'trade_content',
            'legal_content',
            'payment_content',
        )

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]


class ContractApprovalCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    document_data = DocumentCreateSerializer(many=True, required=False)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = ContractApproval
        fields = (
            'title',
            'opportunity_id',
            'opportunity_data',
            'employee_inherit_id',
            'employee_inherit_data',
            'document_data',
            'attachment',
            'abstract_content',
            'trade_content',
            'legal_content',
            'payment_content',
        )

    @classmethod
    def validate_opportunity_id(cls, value):
        return ContractValid.validate_opportunity_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return ContractValid.validate_employee_inherit_id(value=value)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = ContractAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        contract = ContractApproval.objects.create(**validated_data)
        ContractCommonCreate.handle_attach_file(instance=contract, attachment_result=attachment)
        ContractCommonCreate.create_sub_models(validated_data=validated_data, instance=contract)
        return contract


class ContractApprovalUpdateSerializer(AbstractCreateSerializerModel):
    document_data = DocumentCreateSerializer(many=True, required=False)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = ContractApproval
        fields = (
            'title',
            'opportunity_id',
            'opportunity_data',
            'employee_inherit_id',
            'employee_inherit_data',
            'document_data',
            'attachment',
            'abstract_content',
            'trade_content',
            'legal_content',
            'payment_content',
        )

    @classmethod
    def validate_opportunity_id(cls, value):
        return ContractValid.validate_opportunity_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return ContractValid.validate_employee_inherit_id(value=value)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = ContractAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=self.instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        ContractCommonCreate.handle_attach_file(instance=instance, attachment_result=attachment)
        ContractCommonCreate.create_sub_models(validated_data=validated_data, instance=instance)
        return instance
