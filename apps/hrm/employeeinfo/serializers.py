from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.hrm.employeeinfo.models import EmployeeInfo, EmployeeHRNotMapEmployeeHRM
from apps.shared import HRMsg, DisperseModel, HrMsg
from apps.shared.translations.hrm import HRMMsg


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

    @classmethod
    def validate_employee(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

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
                else:
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
            company = self.context.get('company_current', None)
            tenant = self.context.get('tenant_current', None)
            employee = DisperseModel(app_model='hr.Employee').get_model().objects.create(
                code=attrs['code'],
                first_name=attrs['first_name'],
                last_name=attrs['last_name'],
                email=attrs['email'],
                phone=attrs['phone'],
                date_joined=attrs['date_joined'],
                company_id=str(company.id),
                tenant_id=str(tenant.id)
            )
            EmployeeHRNotMapEmployeeHRM.objects.create(
                company=employee.company,
                employee=employee,
                is_mapped=False
            )
            emp_is_map = employee

        for e in ['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined']:
            attrs.pop(e)
        return emp_is_map

    def create(self, validated_data):
        obj_employee = self.check_is_map(validated_data)
        pk = validated_data.pop('employee_create', None)
        validated_data['employee'] = obj_employee
        if pk:
            validated_data['id'] = pk
        info = EmployeeInfo.objects.create(**validated_data)
        if info:
            emp_map = info.employee.employee_hr.all()
            for emp in emp_map:
                emp.is_mapped = True
                emp.save(update_fields=['is_mapped'])
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
            'title': obj.place_of_birth.title
        } if obj.place_of_birth else {}

    @classmethod
    def get_place_of_origin(cls, obj):
        return {
            'id': str(obj.place_of_origin.id),
            'title': obj.place_of_origin.title
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
        )


class EmployeeInfoUpdateSerializers(serializers.ModelSerializer):
    employee = serializers.UUIDField()
    first_name = serializers.CharField(max_length=500)
    last_name = serializers.CharField(max_length=500)
    email = serializers.CharField(max_length=500)
    phone = serializers.IntegerField()
    date_joined = serializers.DateField()
    dob = serializers.DateField(required=False)
    code = serializers.CharField(max_length=500)

    @classmethod
    def validate_employee(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': HrMsg.EMPLOYEE_NOT_FOUND})

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
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'dob',
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
            is_emp.dob = attrs['dob']
            is_emp.save(update_fields=['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined'])
            for e in ['code', 'first_name', 'last_name', 'email', 'phone', 'date_joined', 'dob']:
                attrs.pop(e)

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                self.update_hr_employee(validated_data)
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save()
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
