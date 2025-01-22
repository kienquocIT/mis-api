__all__ = ['EmployeeContractListSerializers', 'EmployeeContractCreateSerializers', 'EmployeeContractDetailSerializers',
           'EmployeeContractRuntimeCreateSerializers']

from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.shared import HRMsg
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.hrm import HRMMsg
from ..models import EmployeeContract, EmployeeContractMapAttachment, EmployeeContractRuntime


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


class EmployeeContractRuntimeCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContractRuntime
        fields = (
            'employee_contract',
            'members',
            'contract',
            'signatures',
        )

    @classmethod
    def validate_employee_contract(cls, value):
        if value and value.sign_status > 0:
            raise serializers.ValidationError({'employee_contract': HRMMsg.RUNTIME_CONTRACT_FIELD_ERROR})
        return value

    @classmethod
    def validate_members(cls, value):
        employee_list = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=value
        )
        if employee_list.count() == len(value):
            return [
                {'id': str(employee.id), 'full_name': employee.get_full_name(2)}
                for employee in employee_list
            ]
        raise serializers.ValidationError({'employee_list': HRMsg.MEMBER_NOT_FOUND})

    @classmethod
    def validate_signatures(cls, value):
        employee_in_sign = []
        for key in value:
            item = value[key]
            employee_in_sign += item.get('assignee', [])
        employee_list = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=employee_in_sign
        )
        if employee_list.count() < len(employee_in_sign):
            raise serializers.ValidationError({'employee_list': HRMMsg.RUNTIME_CONTRACT_FIELD_ERROR})
        return value

    def create(self, validated_data):
        validated_data['employee_created'] = self.context.get('user', None)
        try:
            with transaction.atomic():
                # update contract status is signing
                employee_contract = validated_data.get('employee_contract', None)
                info = EmployeeContractRuntime.objects.create(**validated_data)
                if info:
                    employee_contract.update(sign_status=1)
                return info
        except Exception as err:
            return err


class EmployeeContractRuntimeDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmployeeContractRuntime
        fields = (
            'id',
            'employee_contract',
            'members',
            'contract',
            'signatures',
        )
