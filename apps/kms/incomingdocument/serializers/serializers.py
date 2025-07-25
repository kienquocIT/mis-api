from django.db import transaction
from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.kms.incomingdocument.models import (
    KMSIncomingDocument, IncomingAttachDocumentMapAttachFile,
    KMSAttachIncomingDocuments, KMSInternalRecipientIncomingDocument
)
from apps.shared import (
    AbstractCreateSerializerModel, KMSMsg, AbstractDetailSerializerModel, AttachmentMsg,
    SECURITY_LEVEL, SerializerCommonValidate, SerializerCommonHandle, AbstractListSerializerModel, BaseMsg
)


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
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


def create_attached_incoming_document(incoming_doc, attached_list):
    new_list = []
    for item in attached_list:
        incoming_doc_attachments = item.pop('attachment', [])

        if 'id' not in item:
            create_attachment(incoming_doc.id, incoming_doc_attachments)

        # validate date
        effective_date = item.get('effective_date', None)
        expired_date = item.get('expired_date', None)
        if effective_date and expired_date and expired_date <= effective_date:
            raise serializers.ValidationError({
                'expired_date': KMSMsg.EXPIRED_DATE_ERROR
            })

        temp = KMSAttachIncomingDocuments(
            title='',
            incoming_document_id=str(incoming_doc.id),
            document_type_id=item.get('document_type'),
            content_group_id=item.get('content_group'),
            sender=item.get('sender'),
            effective_date=effective_date,
            expired_date=expired_date,
            security_level=item.get('security_level'),
            company=incoming_doc.company,
            tenant=incoming_doc.tenant
        )
        new_list.append(temp)
    KMSAttachIncomingDocuments.objects.filter_on_company(incoming_document=incoming_doc).delete()
    KMSAttachIncomingDocuments.objects.bulk_create(new_list)
    return True


def create_internal_recipient(incoming_doc, internal_list):
    new_list = []
    for item in internal_list:
        new_list.append(KMSInternalRecipientIncomingDocument(
            incoming_document=incoming_doc,
            **item
        ))
    KMSInternalRecipientIncomingDocument.objects.filter(incoming_document=incoming_doc).delete()
    KMSInternalRecipientIncomingDocument.objects.bulk_create(new_list)
    return True


class KMSIncomingDocumentListSerializer(AbstractListSerializerModel):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'code',
            'title',
            'remark',
            'sender',
            'date_created',
        )

    @classmethod
    def get_sender(cls, obj):
        for item in obj.kms_attach_incoming_documents.all():
            return item.sender
        return ''


class KMSAttachedIncomingDocumentSerializers(serializers.Serializer):
    sender = serializers.CharField(max_length=100)
    document_type = serializers.UUIDField(required=False, allow_null=True)
    content_group = serializers.UUIDField(required=False, allow_null=True)
    effective_date = serializers.DateField(required=False, allow_null=True)
    expired_date = serializers.DateField(required=False, allow_null=True)
    security_level = serializers.IntegerField(required=False, allow_null=True)


class KMSInternalRecipientIncomingDocumentSerializers(serializers.ModelSerializer):
    employee = serializers.UUIDField()

    class Meta:
        model = KMSInternalRecipientIncomingDocument
        fields = (
            'employee',
            'employee_access',
        )

    @classmethod
    def validate_employee(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': BaseMsg.NOT_EXIST})


class KMSIncomingDocumentCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attached_list = KMSAttachedIncomingDocumentSerializers(many=True)
    internal_recipient = KMSInternalRecipientIncomingDocumentSerializers(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=IncomingAttachDocumentMapAttachFile, value=value
        )

    @decorator_run_workflow
    def create(self, validate_data):
        with transaction.atomic():
            attached_list = validate_data.pop('attached_list', [])
            internal_list = validate_data.pop('internal_recipient', [])
            attachment = validate_data.pop('attachment', [])
            incoming_doc = KMSIncomingDocument.objects.create(**validate_data)
            create_attached_incoming_document(incoming_doc, attached_list)
            create_internal_recipient(incoming_doc, internal_list)
            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="6944d486-66a0-4521-bd28-681d5df42ff3").first(),
                model_cls=IncomingAttachDocumentMapAttachFile,
                instance=incoming_doc,
                attachment_result=attachment,
            )
            return incoming_doc

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'title',
            'attached_list',
            'remark',
            'internal_recipient',
            'attachment',
        )


class KMSIncomingDocumentDetailSerializer(AbstractDetailSerializerModel):
    attached_list = serializers.SerializerMethodField()
    internal_recipient = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

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
                'employee': item.employee.id,
                'employee_access': item.employee_access,
            })
        return res_list

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'id',
            'title',
            'remark',
            'employee_inherit',
            'attached_list',
            'internal_recipient',
            'attachment',
        )


class KMSIncomingDocumentUpdateSerializer(AbstractCreateSerializerModel):
    attached_list = KMSAttachedIncomingDocumentSerializers(many=True)
    internal_recipient = KMSInternalRecipientIncomingDocumentSerializers(many=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    @classmethod
    def validate_internal_recipient(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': KMSMsg.INTERNAL_RECIPIENT_NOT_FOUND})
        return value

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=IncomingAttachDocumentMapAttachFile, value=value, doc_id=self.instance.id
        )

    @decorator_run_workflow
    def update(self, instance, validated_data):
        with transaction.atomic():
            attached_list = validated_data.pop('attached_list', [])
            internal_list = validated_data.pop('internal_recipient', [])
            attachment = validated_data.pop('attachment', [])
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            create_attached_incoming_document(instance, attached_list)
            create_internal_recipient(instance, internal_list)
            SerializerCommonHandle.handle_attach_file(
                relate_app=Application.objects.filter(id="6944d486-66a0-4521-bd28-681d5df42ff3").first(),
                model_cls=IncomingAttachDocumentMapAttachFile,
                instance=instance,
                attachment_result=attachment,
            )
            return instance

    class Meta:
        model = KMSIncomingDocument
        fields = (
            'title',
            'attached_list',
            'remark',
            'internal_recipient',
            'attachment',
        )
