from django.db import transaction
from rest_framework import serializers
from apps.core.base.models import Application

from apps.core.workflow.tasks import decorator_run_workflow
from apps.kms.incomingdocument.models import KMSIncomingDocument, IncomingAttachDocumentMapAttachFile, \
    KMSAttachIncomingDocuments, KMSInternalRecipientIncomingDocument
from apps.shared import AbstractCreateSerializerModel, KMSMsg, AbstractDetailSerializerModel, AttachmentMsg, HRMsg, \
    SECURITY_LEVEL

__all__ = [
    'KMSIncomingDocumentListSerializer',
    'KMSAttachedIncomingDocumentSerializers',
    'KMSInternalRecipientIncomingDocumentSerializers',
    'KMSIncomingDocumentCreateSerializer',
    'KMSIncomingDocumentDetailSerializer'
]


def create_attachment(doc_id, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="6944d486-66a0-4521-bd28-681d5df42ff3")
        state = IncomingAttachDocumentMapAttachFile.resolve_change(
            result=attachment_result,
            doc_id=doc_id,
            doc_app=relate_app
        )
        if state:
            return True
        raise serializers.ValidationError({'attchment': AttachmentMsg.ERROR_VERIFY})
    return True


def create_attached_incoming_document(incoming_doc, attached_list):
    KMSAttachIncomingDocuments.objects.filter_on_company(incoming_document=incoming_doc).delete()
    new_list = []
    for item in attached_list:
        incoming_doc_attachments = item.pop('attachment', [])
        total_attach = [str(val.id) for val in incoming_doc_attachments.get('new', [])]
        total_attach += [str(val.id) for val in incoming_doc_attachments.get('keep', [])]

        if 'id' not in item:
            create_attachment(incoming_doc.id, incoming_doc_attachments)
        temp = KMSAttachIncomingDocuments(
            title='',
            incoming_document_id=str(incoming_doc.id),
            document_type_id=item.get('document_type'),
            content_group_id=item.get('content_group'),
            sender=item.get('sender'),
            effective_date=item.get('effective_date'),
            expired_date=item.get('expired_date'),
            security_level=item.get('security_level'),
            attachment=total_attach,
            company=incoming_doc.company,
            tenant=incoming_doc.tenant
        )
        new_list.append(temp)
    KMSAttachIncomingDocuments.objects.bulk_create(new_list)


def create_internal_recipient(incoming_doc, internal_list):
    KMSInternalRecipientIncomingDocument.objects.filter_on_company(incoming_document_id=str(incoming_doc.id)).delete()
    new_list = []
    for item in internal_list:
        item_content = KMSInternalRecipientIncomingDocument(
            title=item.get('title'),
            incoming_document_id=str(incoming_doc.id),
            kind=item.get('kind', 2),
            employee_access=item.get('employee_access', {}),
            group_access=item.get('group_access', {}),
            document_permission_list=item['document_permission_list'],
            expiration_date=item.get('expiration_date'),
            company=incoming_doc.company,
            tenant=incoming_doc.tenant,
        )
        new_list.append(item_content)
    KMSInternalRecipientIncomingDocument.objects.bulk_create(new_list)


class KMSIncomingDocumentListSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'sender'
        )

    @classmethod
    def get_sender(cls, obj):
        for item in obj.kms_attach_incoming_documents.all():
            return item.sender
        return ''


class KMSAttachedIncomingDocumentSerializers(serializers.Serializer):
    attachment = serializers.ListSerializer(child=serializers.UUIDField())
    sender = serializers.CharField(max_length=100)
    document_type = serializers.UUIDField(required=False, allow_null=True)
    content_group = serializers.UUIDField(required=False, allow_null=True)
    effective_date = serializers.DateField(required=False, allow_null=True)
    expired_date = serializers.DateField(required=False, allow_null=True)
    security_level = serializers.IntegerField(required=False, allow_null=True)

    # def validate_attachment(self, attrs):
    #     user = self.context.get('user', None)
    #     if user and hasattr(user, 'employee_current_id'):
    #         state, result = IncomingAttachDocumentMapAttachFile.valid_change(
    #             current_ids=[str(idx) for idx in attrs],
    #             employee_id=user.employee_current_id,
    #             doc_id=None
    #         )
    #         if state is True:
    #             return result
    #         raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
    #     raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})


class KMSInternalRecipientIncomingDocumentSerializers(serializers.Serializer):
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
        raise serializers.ValidationError({
            'document_permission_list': KMSMsg.RECIPIENT_PERMISSION_ERROR
        })


class KMSIncomingDocumentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    attached_list = KMSAttachedIncomingDocumentSerializers(many=True)
    internal_recipient = KMSInternalRecipientIncomingDocumentSerializers(many=True)

    # @classmethod
    # def validate_attached_list(cls, value):
    #     if not len(value) > 0:
    #         raise serializers.ValidationError({'detail': AttachmentMsg.FILE_NOT_FOUND})
    #     return value

    def validate_attachment(self, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': AttachmentMsg.FILE_NOT_FOUND})
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = IncomingAttachDocumentMapAttachFile.valid_change(
                current_ids=value,
                employee_id=user.employee_current_id,
                doc_id=self.instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    # def validate_attachment(self, attrs):
    #     user = self.context.get('user', None)
    #     if user and hasattr(user, 'employee_current_id'):
    #         state, result = IncomingAttachDocumentMapAttachFile.valid_change(
    #             current_ids=[str(idx) for idx in attrs],
    #             employee_id=user.employee_current_id,
    #             doc_id=None
    #         )
    #         if state is True:
    #             return result
    #         raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
    #     raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @decorator_run_workflow
    def create(self, validate_data):
        with transaction.atomic():
            attached_list = validate_data.pop('attached_list', None)
            internal_list = validate_data.pop('internal_recipient', None)
            incoming_doc = KMSIncomingDocument.objects.create(**validate_data)
            create_attached_incoming_document(incoming_doc, attached_list)
            create_internal_recipient(incoming_doc, internal_list)
            return incoming_doc

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'title',
            'attached_list',
            'remark',
            'internal_recipient'
        )


class KMSIncomingDocumentDetailSerializer(AbstractDetailSerializerModel):
    attached_list = serializers.SerializerMethodField()
    internal_recipient = serializers.SerializerMethodField()

    @classmethod
    def get_attached_list(cls, obj):
        item_list = obj.kms_attach_incoming_documents.all().select_related(
            'document_type',
            'content_group',
        )
        attr_lst = []
        att_objs = IncomingAttachDocumentMapAttachFile.objects.select_related('attachment') \
            .filter(incoming_document=obj)
        for item in item_list:
            att_lst = att_objs.filter(attachment_id__in=item.attachment)
            attr_lst.append({
                'id': item.id,
                # 'title': item.title,
                'sender': item.sender,
                'document_type': {
                    'id': item.document_type.id,
                    'title': item.document_type.title
                } if item.document_type else {},
                'content_group': {
                    'id': item.content_group.id,
                    'title': item.content_group.title
                } if item.content_group else {},
                'security_level': dict(SECURITY_LEVEL).get(item.security_level, 'Unknown'),
                'effective_date': item.effective_date,
                'expired_date': item.expired_date,
                'attachment': [att.attachment.get_detail() for att in att_lst]
            })
        return attr_lst

    @classmethod
    def get_internal_recipient(cls, obj):
        item_list = obj.kms_kmsinternalrecipient_incoming_doc.all()
        res_list = []
        for item in item_list:
            res_list.append({
                'id': item.id,
                'title': item.title,
                'kind': item.kind,
                'employee_access': item.employee_access,
                'group_access': item.group_access,
                'document_permission_list': item.document_permission_list,
                'expiration_date': item.expiration_date
            })
        return res_list

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'employee_inherit',
            'attached_list',
            'internal_recipient',
        )


class KMSIncomingDocumentUpdateSerializer(AbstractCreateSerializerModel):
    attached_list = KMSAttachedIncomingDocumentSerializers(many=True)
    internal_recipient = KMSInternalRecipientIncomingDocumentSerializers(many=True)

    @classmethod
    def validate_attached_list(cls, context_user, doc_id, validate_data):
        if 'attached_list' in validate_data:
            if validate_data.get('attached_list'):
                if context_user and hasattr(context_user, 'employee_current_id'):
                    state, result = IncomingAttachDocumentMapAttachFile.valid_change(
                        current_ids=validate_data.get('attached_list', []),
                        employee_id=context_user.employee_current_id,
                        doc_id=doc_id
                    )
                    if state is True:
                        validate_data['attached_list'] = result
                    else:
                        raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
                else:
                    raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})
        print('11. validate_attachment --- ok')
        return validate_data

    # def validate_attached_list(self, value):
    #     if not len(value) > 0:
    #         raise serializers.ValidationError({'detail': AttachmentMsg.FILE_NOT_FOUND})
    #
    #     user = self.context.get('user', None)
    #     if user and hasattr(user, 'employee_current_id'):
    #         state, result = IncomingAttachDocumentMapAttachFile.valid_change(
    #             current_ids=value,
    #             employee_id=user.employee_current_id,
    #             doc_id=self.instance.id
    #         )
    #         if state is True:
    #             return result
    #         raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
    #     raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})


    # def validate_attachment(self, attrs):
    #     user = self.context.get('user', None)
    #     if user and hasattr(user, 'employee_current_id'):
    #         state, result = IncomingAttachDocumentMapAttachFile.valid_change(
    #             current_ids=[str(idx) for idx in attrs],
    #             employee_id=user.employee_current_id,
    #             doc_id=None
    #         )
    #         if state is True:
    #             return result
    #         raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
    #     raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})


    @classmethod
    def validate_internal_recipient(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': KMSMsg.INTERNAL_RECIPIENT_NOT_FOUND})
        return value

    @decorator_run_workflow
    def update(self, instance, validated_data):
        with transaction.atomic():
            attached_list = validated_data.pop('attached_list', [])
            internal_list = validated_data.pop('internal_recipient', [])
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            create_attached_incoming_document(instance, attached_list)
            create_internal_recipient(instance, internal_list)
            return instance

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'title',
            'attached_list',
            'remark',
            'internal_recipient'
        )
