from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.kms.incomingdocument.models import KMSIncomingDocument, IncomingAttachDocumentMapAttachFile
from apps.shared import AbstractCreateSerializerModel, KMSMsg, AbstractDetailSerializerModel, AttachmentMsg, HRMsg


class KMSIncomingDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'sender',
            'document_type',
            'content_group',
            'effective_date',
            'expired_date',
            'security_level'
        )


class KMSIncomingDocumentCreateSerializer(serializers.ModelSerializer):
    attachment = serializers.ListSerializer(child=serializers.UUIDField())
    title = serializers.CharField(max_length=100)
    remark = serializers.CharField()
    sender = serializers.CharField(max_length=100)
    document_type = serializers.UUIDField(required=False, allow_null=True)
    content_group = serializers.UUIDField(required=False, allow_null=True)
    effective_date = serializers.DateField(required=False, allow_null=True)
    expired_date = serializers.DateField(required=False, allow_null=True)

    def validate_attachment(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = IncomingAttachDocumentMapAttachFile.valid_change(
                current_ids=[str(idx) for idx in attrs],
                employee_id=user.employee_current_id,
                doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def create(self, validate_data):
        incoming_doc = KMSIncomingDocument.objects.create(**validate_data)
        return incoming_doc

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'title',
            'remark',
            'sender',
            'document_type',
            'content_group',
            'effective_date',
            'expired_date',
            'security_level'
        )


class KMSIncomingDocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'sender',
            'document_type',
            'content_group',
            'effective_date',
            'expired_date',
            'security_level'
        )
