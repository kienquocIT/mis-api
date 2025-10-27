__all__ = ['EmployeeContractListSerializers', 'EmployeeContractCreateSerializers', 'EmployeeContractDetailSerializers',
           'EmployeeContractRuntimeCreateSerializers', 'EmployeeContractRuntimeUpdateSerializers',
           'EmployeeContractRuntimeDetailSerializers']


from django.db import transaction
from django.utils import timezone
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
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

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
            'content_info',
            'employee_salary_level',
            'employee_salary',
            'employee_salary_insurance',
            'employee_salary_rate',
            'employee_salary_coefficient'
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
            'content_info',
            'employee_salary_level',
            'employee_salary',
            'employee_salary_insurance',
            'employee_salary_rate',
            'employee_salary_coefficient'
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
            id__in=[item.get('id') for item in value]
        )
        if employee_list.count() == len(value):
            return value
        raise serializers.ValidationError({'employee_list': HRMsg.MEMBER_NOT_FOUND})

    @classmethod
    def validate_signatures(cls, value):
        employee_list = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=[item['assignee']['id'] for key, item in value.items()]
        )
        if employee_list.count() < len(value):
            raise serializers.ValidationError({'employee_list': HRMMsg.RUNTIME_CONTRACT_FIELD_ERROR})
        return value

    def create(self, validated_data):
        validated_data['employee_created'] = self.context.get('user', None)
        try:
            with transaction.atomic():
                # update contract status is signing
                employee_contract = validated_data.get('employee_contract', None)
                info = EmployeeContractRuntime.objects.create(**validated_data)
                if info and employee_contract:
                    employee_contract.sign_status = 1
                    employee_contract.save(update_fields=['sign_status'])
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


class EmployeeContractRuntimeUpdateSerializers(serializers.ModelSerializer):
    is_sign = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        model = EmployeeContractRuntime
        fields = (
            'contract',
            'is_sign'
        )

    def sign_and_save(self, stt, emp):
        sign_new_data = self.instance.signatures.copy()
        for key, sign in self.instance.signatures.items():
            if not sign['stt']:
                if sign['assignee']['id'] == str(emp.id):
                    sign_new_data[key]['assignee']['date_sign'] = timezone.now().strftime('%Y-%m-%d, %H:%M:%S')
                    if stt:
                        sign_new_data[key]['assignee']['is_sign'] = stt
                    else:
                        sign_new_data[key]['assignee']['is_reject'] = True
                    # update stt true khi user đã ký or đã từ chối
                    sign_new_data[key]['stt'] = True
                    break
                raise serializers.ValidationError({'employee': HRMMsg.EMPLOYEE_PERMISSION_DENIED})
        if all(item['stt'] for item in sign_new_data.values()):
            self.instance.contract_status = 1
        return sign_new_data

    @classmethod
    def update_back_to_employee_contract(cls, runtime):
        employee_contract = runtime.employee_contract
        employee_contract.content = runtime.contract
        if runtime.contract_status == 1:
            employee_contract.sign_status = 2
        employee_contract.save(update_fields=['sign_status', 'content'])

    def validate(self, attrs):
        if str(self.context.get('user').id) not in list(map(lambda x: x.get('id', ''), self.instance.members)):
            raise serializers.ValidationError({'employee': HRMMsg.EMPLOYEE_PERMISSION_DENIED})

        attrs['signatures'] = self.sign_and_save(
            attrs.pop('is_sign', False),
            self.context.get('user', None)
        )
        return attrs

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        self.update_back_to_employee_contract(instance)
        return instance
