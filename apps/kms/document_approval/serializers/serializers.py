from django.db import transaction
from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import AttachmentMsg, HRMsg, KMSMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel
from ..models import KMSDocumentApproval, AttachDocumentMapAttachmentFile, KMSInternalRecipient, KSMAttachedDocuments


def create_attachment(doc_id, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="7505d5db-42fe-4cde-ae5e-dbba78e2df03")
        state = AttachDocumentMapAttachmentFile.resolve_change(
            result=attachment_result, doc_id=doc_id.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


def create_attached_document(document_appr, attached_list):
    KSMAttachedDocuments.objects.filter_on_company(document_approval=document_appr).delete()
    new_list = []
    for item in attached_list:
        attachments = item.pop('attachment', [])
        create_attachment(document_appr, attachments)
        new_list.append(KSMAttachedDocuments(
            title=item.get('title'),
            document_approval_id=str(document_appr.id),
            document_type_id=item.get('document_type'),
            content_group_id=item.get('content_group'),
            security_lv=item.get('security_lv'),
            published_place_id=item.get('group'),
            effective_date=item.get('effective_date'),
            expired_date=item.get('expired_date'),
            folder_id=item.get('folder'),
            attachment=[str(val.id) for val in attachments.get('new', [])],
            company=document_appr.company,
            tenant=document_appr.tenant
        ))
    KSMAttachedDocuments.objects.bulk_create(new_list)


def create_internal_recipient(doc_obj, internal_list):
    # // delete all recipient before and create new
    KMSInternalRecipient.objects.filter_on_company(document_approval_id=str(doc_obj.id)).delete()
    new_list = []
    for item in internal_list:
        new_list.append(
            KMSInternalRecipient(
                title=item.get('title'),
                document_approval_id=str(doc_obj.id),
                kind=item.get('kind', 2),
                employee_access=item.get('employee_access', {}),
                group_access=item.get('group_access', {}),
                document_permission_list=item['document_permission_list'],
                expiration_date=item.get('expiration_date'),
                company=doc_obj.company,
                tenant=doc_obj.tenant,
            )
        )
    KMSInternalRecipient.objects.bulk_create(new_list)

class KMSAttachedDocumentSerializers(serializers.Serializer):  # noqa
    attachment = serializers.ListSerializer(child=serializers.UUIDField())
    title = serializers.CharField(required=False, allow_null=True)
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
    title = serializers.CharField(required=False, allow_null=True)
    kind = serializers.IntegerField()
    employee_access = serializers.JSONField(required=False, allow_null=True)
    group_access = serializers.JSONField(required=False, allow_null=True)
    document_permission_list = serializers.JSONField()
    expiration_date = serializers.DateField(required=False, allow_null=True)

    @classmethod
    def validate_document_permission_list(cls, attrs):
        if len(attrs) > 0:
            return attrs
        raise serializers.ValidationError({'document_permission_list': KMSMsg.RECIPIENT_PERMISSION_ERROR})


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
            'id',
            'title',
            'remark',
            'code',
            'system_status',
        )


class KMSDocumentApprovalDetailSerializer(AbstractDetailSerializerModel):
    attached_list = serializers.SerializerMethodField()
    internal_recipient = serializers.SerializerMethodField()

    @classmethod
    def get_attached_list(cls, obj):
        item_list = obj.kms_kmsattached_document_approval.all().select_related(
            'document_type', 'content_group', 'published_place', 'folder'
        )
        attr_lst = []
        att_objs = AttachDocumentMapAttachmentFile.objects.select_related('attachment').filter(document_approval=obj)
        for item in item_list:
            att_lst = att_objs.filter(attachment_id__in=item.attachment)
            attr_lst.append({
                'id': item.id,
                'title': item.title,
                'document_type': {
                    'id': item.document_type.id,
                    'title': item.document_type.title
                } if item.document_type else {},
                'content_group': {
                    'id': item.content_group.id,
                    'title': item.content_group.title
                } if item.content_group else {},
                'security_lv': item.security_lv,
                'published_place': {
                    'id': item.published_place.id,
                    'title': item.published_place.title,
                    'code': item.published_place.code
                } if item.published_place else {},
                'effective_date': item.effective_date,
                'expired_date': item.expired_date,
                'folder': {
                    'id': item.folder.id,
                    'title': item.folder
                } if item.folder else {},
                'attachment': [att.attachment.get_detail() for att in att_lst]
            })
        return attr_lst

    @classmethod
    def get_internal_recipient(cls, obj):
        item_list = obj.kms_kmsinternalrecipient_doc_apr.all()
        itn_list = []
        for item in item_list:
            itn_list.append({
                'id': item.id,
                'title': item.title,
                'kind': item.kind,
                'employee_access': item.employee_access,
                'group_access': item.group_access,
                'document_permission_list': item.document_permission_list,
                'expiration_date': item.expiration_date,
            })
        return itn_list

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "full_name": obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    class Meta:
        model = KMSDocumentApproval
        fields = (
            'id',
            'title',
            'remark',
            'system_status',
            'employee_inherit',
            'attached_list',
            'internal_recipient',
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
