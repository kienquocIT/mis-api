__all__ = ['EmployeeContractListSerializers', 'EmployeeContractCreateSerializers', 'EmployeeContractDetailSerializers']

from rest_framework import serializers

from apps.shared import HRMsg
from apps.shared.translations.base import AttachmentMsg
from ..models import EmployeeContract, EmployeeContractMapAttachment


class EmployeeContractListSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContract
        fields = (
            'id',
            'code',
            'contract_type',
            'expired_date',
            'effected_date',
            'sign_status'
        )


class EmployeeContractCreateSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    @classmethod
    def validate_employee_info(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_represent(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    def validate_attachment(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = EmployeeContractMapAttachment.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    class Meta:
        model = EmployeeContract
        fields = (
            'id',
            'employee_info',
            'contract_type',
            'limit_time',
            'effected_date',
            'expired_date',
            'signing_date',
            'represent',
            'file_type',
            'attachment',
            'content',
            'sign_status',
        )


class EmployeeContractDetailSerializers(serializers.ModelSerializer):
    represent = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    @classmethod
    def get_represent(cls, obj):
        if obj.represent and hasattr(obj.represent, 'get_detail_minimal'):
            return obj.represent.get_detail_minimal()
        return {}

    @classmethod
    def get_attachment(cls, obj):
        att_objs = EmployeeContractMapAttachment.objects.select_related('attachment').filter(employee_contract=obj)
        return [item.attachment.get_detail() for item in att_objs]

    class Meta:
        model = EmployeeContract
        fields = (
            'id',
            'contract_type',
            'limit_time',
            'effected_date',
            'expired_date',
            'signing_date',
            'represent',
            'file_type',
            'attachment',
            'content',
            'sign_status',
        )
