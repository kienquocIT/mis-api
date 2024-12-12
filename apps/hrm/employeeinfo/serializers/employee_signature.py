from rest_framework import serializers

from apps.core.base.models import Application
from apps.shared import HRMsg
from apps.shared.translations.base import AttachmentMsg
from ..models import EmployeeInfo, EmployeeMapSignatureAttachment


def handle_attachment(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="7436c857-ad09-4213-a190-c1c7472e99be")
        state = EmployeeMapSignatureAttachment.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


class EmployeeSignatureUpdateAttachmentSerializers(serializers.ModelSerializer):

    class Meta:
        model = EmployeeInfo
        fields = (
            '__all__'
        )

    def validate_attachment(self, attrs):
        user = self.context.get('user', None)
        instance = self.instance
        if user and hasattr(user, 'employee_current_id'):
            state, result = EmployeeMapSignatureAttachment.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if attachment is not None:
            handle_attachment(instance, attachment)
        return instance


class EmployeeSignatureAttachmentListSerializers(serializers.ModelSerializer):
    signature = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'signature'
        )

    @classmethod
    def get_signature(cls, obj):
        att_objs = EmployeeMapSignatureAttachment.objects.select_related('attachment').filter(employee_info=obj)
        return [item.attachment.get_detail(has_link=True) for item in att_objs]
