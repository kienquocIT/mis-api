from django.db import transaction
from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import AttachmentMsg, HRMsg, KMSMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel
from ..models import KMSDocumentApproval, AttachDocumentMapAttachmentFile, KMSInternalRecipient, KSMAttachedDocuments


def create_attachment(doc_id, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="08e41084-4379-4778-9e16-c09401f0a66e")
        state = AttachDocumentMapAttachmentFile.resolve_change(
            result=attachment_result, doc_id=doc_id.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


def create_attached_document(document_appr, attached_list):
    KSMAttachedDocuments.objects.filter(document_approval=document_appr).delete()
    attachments = attached_list.pop('attachments')
    create_attachment(document_appr, attachments)

    new_list = []
    for item in attached_list:
        new_list.append(KSMAttachedDocuments(
            title=item['title'],
            document_approval=document_appr,
            document_type=item['doc_type'],
            content_group=item['content_group'],
            security_lv=item['security_lv'] if 'security' in item else None,
            published_place=item['group'] if 'group' in item else None,
            effective_date=item['effective_date'],
            expired_date=item['expired_date'],
            folder=item['folder'],
            attachment=attachments
        ))
    KSMAttachedDocuments.objects.bulk_create(new_list)


def create_internal_recipient(doc_obj, internal_list):
    KMSInternalRecipient.objects.filter(document_approval_id=str(doc_obj.id)).delete()
    new_list = []
    for item in internal_list:
        new_list.append(
            KMSInternalRecipient(
                document_approval_id=str(doc_obj.id),
                kind=item['kind'],
                employee_access=item['employee_access'] if 'employee_access' in item else {},
                group_access=item['group_access'] if 'group_access' in item else {},
                document_permission_list=item['permission_list'],
                expiration_date=item['expiration_date']
            )
        )
    KMSInternalRecipient.objects.bulk_create(new_list)

class KMSAttachedDocumentSerializers(serializers.Serializer):  # noqa
    attachment = serializers.ListSerializer(child=serializers.UUIDField())
    document_type = serializers.UUIDField(required=False, allow_null=True)
    content_group = serializers.UUIDField(required=False, allow_null=True)
    security_lv = serializers.IntegerField(required=False, allow_null=True)
    published_place = serializers.UUIDField(required=False, allow_null=True)
    effective_date = serializers.DateField(required=False, allow_null=True)
    expired_date = serializers.DateField(required=False, allow_null=True)
    folder = serializers.UUIDField(required=False, allow_null=True)

    def validate_attachment(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = AttachDocumentMapAttachmentFile.valid_change(
                current_ids=[str(idx) for idx in attrs], employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})


class KMSInternalRecipientSerializers(serializers.Serializer):  # noqa
    kind = serializers.IntegerField()
    employee_access = serializers.JSONField(required=False, allow_null=True)
    group_access = serializers.JSONField(required=False, allow_null=True)
    document_permission_list = serializers.JSONField()
    expiration_date = serializers.DateField(required=False, allow_null=True)


class KMSDocumentApprovalCreateSerializer(AbstractCreateSerializerModel):
    attached_list = KMSAttachedDocumentSerializers(many=True)
    internal_recipient = KMSInternalRecipientSerializers(many=True)

    @classmethod
    def validate_attached_list(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': AttachmentMsg.FILE_NOT_FOUND})
        return value

    @classmethod
    def validate_internal_recipient(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': KMSMsg.INTERNAL_RECIPIENT_NOT_FOUND})
        return value

    @decorator_run_workflow
    def create(self, validated_data):
        try:
            with transaction.atomic():
                attached_list = validated_data.pop('attached_list', None)
                internal_list = validated_data.pop('internal_recipient', None)
                document_appr = KMSDocumentApproval.objects.create(**validated_data)
                create_attached_document(document_appr, attached_list)
                create_internal_recipient(document_appr, internal_list)
                return document_appr
        except ValueError as err:
            print('create document approval error, ', err)
            raise serializers.ValidationError({'detail': KMSMsg.CREATE_APPROVAL_ERROR})

    class Meta:
        model = KMSDocumentApproval
        fields = (
            'title',
            'remark',
            'attached_list',
            'internal_recipient',
        )


class KMSDocumentApprovalListSerializer(serializers.ModelSerializer):

    class Meta:
        model = KMSDocumentApproval
        fields = (
            'title',
            'remark',
            'system_status',
        )


class KMSDocumentApprovalDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = KMSDocumentApproval
        fields = (
            'id',
            'title',
            'remark',
            'system_status',
        )


class KMSDocumentApprovalUpdateSerializer(AbstractCreateSerializerModel):
    attached_list = KMSAttachedDocumentSerializers(many=True)
    internal_recipient = KMSInternalRecipientSerializers(many=True)

    class Meta:
        model = KMSDocumentApproval
        fields = (
            'id',
            'title',
            'remark',
            'attached_list',
            'internal_recipient',
        )

    @classmethod
    def validate_attached_list(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': AttachmentMsg.FILE_NOT_FOUND})
        return value

    @classmethod
    def validate_internal_recipient(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': KMSMsg.INTERNAL_RECIPIENT_NOT_FOUND})
        return value

    @decorator_run_workflow
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                attached_list = validated_data.pop('attached_list', None)
                internal_list = validated_data.pop('internal_recipient', None)
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save()
                create_attached_document(instance, attached_list)
                create_internal_recipient(instance, internal_list)
                return instance
        except ValueError as err:
            print('update document approval error, ', err)
            raise serializers.ValidationError({'detail': KMSMsg.CREATE_APPROVAL_ERROR})
