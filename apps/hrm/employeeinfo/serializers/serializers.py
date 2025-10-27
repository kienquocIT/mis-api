from django.utils import timezone
from django.db import transaction
from rest_framework import serializers, exceptions

from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.hrm import HRMMsg
from apps.shared import HRMsg, DisperseModel, HrMsg

from .employee_contract import EmployeeContractCreateSerializers
from ..models import EmployeeInfo, EmployeeHRNotMapEmployeeHRM, EmployeeContractMapAttachment, EmployeeContract, \
    EmployeeMapSignatureAttachment


def handle_attach_file_contract(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="1b8a6f6e-65ec-4769-acaa-465bed2d0523")
        state = EmployeeContractMapAttachment.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


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


class EmployeeInfoListSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee and hasattr(obj.employee, 'get_detail_minimal'):
            return obj.employee.get_detail_minimal()
        return {}

    @classmethod
    def get_user(cls, obj):
        return {
            'id': str(obj.employee.user.id),
            'username': obj.employee.user.username,
            'first_name': obj.employee.user.first_name,
            'last_name': obj.employee.user.last_name
        } if obj.employee.user else {}

    @classmethod
    def get_date_joined(cls, obj):
        if obj.employee:
            return obj.employee.date_joined
        return None

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'employee',
            'user',
            'date_joined',
        )


class EmployeeInfoCreateSerializers(serializers.ModelSerializer):
    employee_create = serializers.UUIDField(required=False, allow_null=True)
    first_name = serializers.CharField(max_length=500)
    last_name = serializers.CharField(max_length=500)
    email = serializers.CharField(max_length=500)
    phone = serializers.IntegerField()
    date_joined = serializers.DateField()
    code = serializers.CharField(max_length=500)
    dependent_deduction = serializers.JSONField(default=list)
    contract = EmployeeContractCreateSerializers()

    @classmethod
    def validate_employee(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    def validate(self, validate_data):
        contract = validate_data.get('contract', None)
        if contract:
            effected_date = contract.get('effected_date', None)
            expired_date = contract.get('expired_date', None)
            if effected_date and expired_date and expired_date <= effected_date:
                raise serializers.ValidationError({'expired_date': HrMsg.EXPIRED_DATE_ERROR})
        return validate_data

    def check_is_map(self, attrs):
        emp_is_map = False
        if 'employee' in attrs:
            emp = DisperseModel(app_model='hr.Employee').get_model().objects.filter_current(
                id=attrs['employee'].id, fill__company=True
            )
            if emp.exists():
                is_emp = emp.first()
                employee_map = is_emp.employee_hr.all()
                employee_map = employee_map.first()
                if employee_map.is_mapped is True:
                    raise serializers.ValidationError({'employee': HRMMsg.EMPLOYEE_MAPPED})

                emp_is_map = is_emp
                emp_is_map.code = attrs['code']
                emp_is_map.first_name = attrs['first_name']
                emp_is_map.last_name = attrs['last_name']
                emp_is_map.email = attrs['email']
                emp_is_map.phone = attrs['phone']
                emp_is_map.date_joined = attrs['date_joined']
                emp_is_map.save(update_fields=['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined'])
            else:
                raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_NOT_FOUND})
        elif 'employee_create' in attrs:
            employee = DisperseModel(app_model='hr.Employee').get_model().objects.create(
                id=attrs['employee_create'],
                code=attrs['code'],
                first_name=attrs['first_name'],
                last_name=attrs['last_name'],
                email=attrs['email'],
                phone=attrs['phone'],
                date_joined=attrs['date_joined'],
                company_id=self.context.get('company_id', None),
                tenant_id=self.context.get('tenant_id', None)
            )
            EmployeeHRNotMapEmployeeHRM.objects.create(
                company=employee.company,
                employee=employee,
                is_mapped=False
            )
            emp_is_map = employee

        for attr in ['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined']:
            attrs.pop(attr)
        return emp_is_map

    def create_contract(self, contract, emp_info=None):
        attachment = contract.pop('attachment', None)
        obj = None
        emp_frk = contract.get('employee_info', None)
        if contract and (emp_info or emp_frk):
            obj = EmployeeContract.objects.create(
                company_id=self.context.get('company_id', None),
                tenant_id=self.context.get('tenant_id', None),
                employee_created_id=self.context.get('user', None).employee_current_id,
                effected_date=contract.get('effected_date') or timezone.now(),
                content=contract.get('content', ''),
                contract_type=contract.get('contract_type', None),
                employee_info=emp_frk if emp_frk else emp_info,
                expired_date=contract.get('expired_date', None),
                file_type=contract.get('file_type', 0),
                limit_time=contract.get('limit_time', False),
                represent=contract.get('represent', None),
                signing_date=contract.get('signing_date') or timezone.now(),
                content_info=contract.get('content_info', {}),
                employee_salary_level=contract.get('employee_salary_level', 0),
                employee_salary=contract.get('employee_salary', 0),
                employee_salary_insurance=contract.get('employee_salary_insurance', 0),
                employee_salary_rate=contract.get('employee_salary_rate', 0),
                employee_salary_coefficient=contract.get('employee_salary_coefficient', 1),
            )
        if attachment is not None and obj:
            handle_attach_file_contract(obj, attachment)
        return True

    def create(self, validated_data):
        obj_employee = self.check_is_map(validated_data)
        validated_data.pop('employee_create', None)
        contract = validated_data.pop('contract', None)
        validated_data['employee'] = obj_employee
        info = EmployeeInfo.objects.create(**validated_data)
        if info:
            emp_map = info.employee.employee_hr.all()
            for emp in emp_map:
                emp.is_mapped = True
                emp.save(update_fields=['is_mapped'])
            if contract:
                self.create_contract(contract, info)
        return info

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'code',
            'employee_create',
            'employee',
            'citizen_id',
            'date_of_issue',
            'place_of_issue',
            'place_of_birth',
            'nationality',
            'place_of_origin',
            'ethnicity',
            'religion',
            'gender',
            'marital_status',
            'bank_acc_no',
            'bank_name',
            'acc_name',
            'tax_code',
            'permanent_address',
            'current_resident',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'dependent_deduction',
            # for contract
            'contract',
        )


class EmployeeInfoDetailSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    nationality = serializers.SerializerMethodField()
    place_of_birth = serializers.SerializerMethodField()
    place_of_origin = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee:
            employee = obj.employee.get_detail_minimal()
            if obj.employee.user:
                employee['user'] = {
                    'id': str(obj.employee.user.id),
                    'first_name': obj.employee.user.first_name,
                    'last_name': obj.employee.user.last_name
                }
            else:
                employee['user'] = {}
            employee['date_joined'] = obj.employee.date_joined
            employee['dob'] = obj.employee.dob
            employee['email'] = obj.employee.email
            employee['phone'] = obj.employee.phone
            return employee
        return {}

    @classmethod
    def get_nationality(cls, obj):
        return {
            'id': str(obj.nationality.id),
            'title': obj.nationality.title
        } if obj.nationality else {}

    @classmethod
    def get_place_of_birth(cls, obj):
        return {
            'id': str(obj.place_of_birth.id),
            'title': obj.place_of_birth.fullname
        } if obj.place_of_birth else {}

    @classmethod
    def get_place_of_origin(cls, obj):
        return {
            'id': str(obj.place_of_origin.id),
            'title': obj.place_of_origin.fullname
        } if obj.place_of_origin else {}

    class Meta:
        model = EmployeeInfo
        fields = (
            'id',
            'employee',
            'citizen_id',
            'date_of_issue',
            'place_of_issue',
            'place_of_birth',
            'nationality',
            'place_of_origin',
            'ethnicity',
            'religion',
            'gender',
            'marital_status',
            'bank_acc_no',
            'bank_name',
            'acc_name',
            'tax_code',
            'permanent_address',
            'current_resident',
            'dependent_deduction'
        )


class EmployeeInfoUpdateSerializers(serializers.ModelSerializer):
    employee = serializers.UUIDField()
    first_name = serializers.CharField(max_length=500)
    last_name = serializers.CharField(max_length=500)
    email = serializers.CharField(max_length=500)
    phone = serializers.IntegerField()
    date_joined = serializers.DateField()
    dob = serializers.DateField(required=False, allow_null=True)
    code = serializers.CharField(max_length=500)
    dependent_deduction = serializers.JSONField(default=list)
    contract = EmployeeContractCreateSerializers()

    @classmethod
    def validate_employee(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_NOT_FOUND})

    def validate(self, validate_data):
        contract = validate_data.get('contract', None)
        if contract:
            effected_date = contract.get('effected_date', None)
            expired_date = contract.get('expired_date', None)
            if effected_date and expired_date and expired_date <= effected_date:
                raise serializers.ValidationError({'expired_date': HrMsg.EXPIRED_DATE_ERROR})
        return validate_data

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

    class Meta:
        model = EmployeeInfo
        fields = (
            'code',
            'employee',
            'citizen_id',
            'date_of_issue',
            'place_of_issue',
            'place_of_birth',
            'nationality',
            'place_of_origin',
            'ethnicity',
            'religion',
            'gender',
            'marital_status',
            'bank_acc_no',
            'bank_name',
            'acc_name',
            'tax_code',
            'permanent_address',
            'current_resident',
            'attachment',
            # for employee
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'dob',
            'dependent_deduction',
            # for contract
            'contract',
        )

    @classmethod
    def update_hr_employee(cls, attrs):
        emp = DisperseModel(app_model='hr.Employee').get_model().objects.filter_current(
            id=attrs['employee'].id, fill__company=True, fill__tenant=True
        )
        if emp.exists():
            is_emp = emp.first()
            is_emp.code = attrs['code']
            is_emp.first_name = attrs['first_name']
            is_emp.last_name = attrs['last_name']
            is_emp.email = attrs['email']
            is_emp.phone = attrs['phone']
            is_emp.date_joined = attrs['date_joined']
            is_emp.dob = attrs.get('dob', None)
            is_emp.save(update_fields=['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined', 'dob'])
            for attr in ['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined', 'dob']:
                if attr in attrs:
                    attrs.pop(attr)

    def create_contract(self, attrs):
        contract = attrs.pop('contract', None)
        attachment = contract.pop('attachment', None)
        obj = None
        if contract:
            contract_id = contract.get('id', None)
            sign = contract.get('sign_status', None)
            if sign == 1:
                raise serializers.ValidationError({'contract': HRMsg.UPDATE_CONTRACT_DENIED})
            if contract_id and (sign == 0 or sign is None):
                try:
                    obj = EmployeeContract.objects.get(id=contract_id)
                    obj.effected_date = contract.get('effected_date') or timezone.now()
                    obj.content = contract.get('content', '')
                    obj.contract_type = contract.get('contract_type')
                    obj.expired_date = contract.get('expired_date')
                    obj.file_type = contract.get('file_type')
                    obj.limit_time = contract.get('limit_time')
                    obj.represent = contract.get('represent')
                    obj.signing_date = contract.get('signing_date')
                    obj.content_info = contract.get('content_info') or {}
                    obj.employee_salary_level = contract.get('employee_salary_level', 0)
                    obj.employee_salary = contract.get('employee_salary', 0)
                    obj.employee_salary_insurance = contract.get('employee_salary_insurance', 0)
                    obj.employee_salary_rate = contract.get('employee_salary_rate', 0)
                    obj.employee_salary_coefficient = contract.get('employee_salary_coefficient', 1)
                    obj.save(
                        update_fields=['effected_date', 'content', 'contract_type', 'expired_date', 'file_type',
                                       'limit_time', 'represent', 'signing_date', 'date_modified', 'content_info',
                                       'employee_salary_level', 'employee_salary', 'employee_salary_insurance',
                                       'employee_salary_rate', 'employee_salary_coefficient']
                    )
                except EmployeeContract.DoesNotExist:
                    raise exceptions.NotFound
            else:
                obj = EmployeeContract.objects.create(
                    company_id=self.context.get('company_id', None),
                    tenant_id=self.context.get('tenant_id', None),
                    employee_created_id=self.context.get('user', None).employee_current_id,
                    effected_date=contract.get('effected_date') or timezone.now(),
                    content=contract.get('content', ''),
                    contract_type=contract.get('contract_type'),
                    employee_info=contract.get('employee_info'),
                    expired_date=contract.get('expired_date'),
                    file_type=contract.get('file_type'),
                    limit_time=contract.get('limit_time'),
                    represent=contract.get('represent'),
                    signing_date=contract.get('signing_date'),
                    content_info=contract.get('content_info') or {},
                    employee_salary_level=contract.get('employee_salary_level', 0),
                    employee_salary=contract.get('employee_salary', 0),
                    employee_salary_insurance=contract.get('employee_salary_insurance', 0),
                    employee_salary_rate=contract.get('employee_salary_rate', 0),
                    employee_salary_coefficient=contract.get('employee_salary_coefficient', 1),
                )
        if attachment is not None and obj:
            handle_attach_file_contract(obj, attachment)
        return True

    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', None)
        try:
            with transaction.atomic():
                self.update_hr_employee(validated_data)
                self.create_contract(validated_data)
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save()
                if attachment is not None:
                    handle_attachment(instance, attachment)
                return instance
        except Exception as err:
            return err


class EmployeeHRNotMapHRMListSerializers(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    @classmethod
    def get_employee(cls, obj):
        if obj.employee and hasattr(obj.employee, 'get_detail_minimal'):
            emp = obj.employee.get_detail_minimal()
            emp.update(
                {
                    'email': obj.employee.email,
                    'date_joined': obj.employee.date_joined,
                    'dob': obj.employee.dob,
                    'phone': obj.employee.phone,
                    'code': obj.employee.code
                }
            )
            user = obj.employee.user
            emp['user'] = {
                'id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name
            } if user else {}

            return emp
        return {}

    class Meta:
        model = EmployeeHRNotMapEmployeeHRM
        fields = (
            'employee',
        )
