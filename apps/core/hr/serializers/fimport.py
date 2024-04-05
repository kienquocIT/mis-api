from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import CompanyUserEmployee
from apps.core.hr.models import Group, Employee, GroupLevel, Role, RoleHolder
from apps.shared import HRMsg, BaseMsg, AccountMsg


class GroupLevelImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLevel
        fields = ('id', 'title', 'code')


class GroupLevelImportSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField()

    @classmethod
    def validate_level(cls, value):
        if value and isinstance(value, int) and value > 0:
            if not GroupLevel.objects.filter_current(level=value, fill__company=True).exists():
                return value
            raise serializers.ValidationError({'level': HRMsg.GROUP_LEVEL_EXIST})
        raise serializers.ValidationError({'level': HRMsg.GROUP_LEVEL_OUT_OF_RANGE})

    description = serializers.CharField(max_length=500)

    def create(self, validated_data):
        group_level = GroupLevel.objects.create(**validated_data)
        return group_level

    class Meta:
        model = GroupLevel
        fields = (
            'level',
            'description',
            'first_manager_description',
            'second_manager_description',
        )


class GroupImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'code')


class GroupImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)

    @classmethod
    def validate_code(cls, value):
        if Group.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value
        ).exists():
            raise serializers.ValidationError({'code': HRMsg.GROUP_CODE_EXIST})
        return value

    group_level = serializers.CharField()

    @classmethod
    def validate_group_level(cls, value):
        try:
            return GroupLevel.objects.get_current(fill__company=True, level=value)
        except GroupLevel.DoesNotExist:
            raise serializers.ValidationError({'group_level': HRMsg.GROUP_LEVEL_NOT_EXIST})
        except GroupLevel.MultipleObjectsReturned:
            raise serializers.ValidationError({'group_level': BaseMsg.CAUSE_DUPLICATE})

    parent_n = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_parent_n(cls, value):
        if value:
            try:
                return Group.objects.get_current(fill__company=True, code=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError({'parent_n': HRMsg.GROUP_NOT_EXIST})
            except Group.MultipleObjectsReturned:
                raise serializers.ValidationError({'parent_n': BaseMsg.CAUSE_DUPLICATE})
        return None

    group_employee = serializers.CharField(allow_blank=True, required=False)

    @classmethod
    def validate_group_employee(cls, value) -> None or list:
        if value:
            codes = [item.strip() for item in list(filter(None, value.split(',')))]
            objs = Employee.objects.filter_current(fill__tenant=True, fill__company=True, code__in=codes)
            if objs.count() == len(codes):
                return objs
            raise serializers.ValidationError(
                {
                    'group_employee': HRMsg.EMPLOYEE_NOT_EXIST,
                }
            )
        return None

    first_manager = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_first_manager(cls, value):
        if value:
            try:
                return Employee.objects.get_current(fill__company=True, code=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'first_manager': HRMsg.EMPLOYEE_NOT_EXIST})
            except Employee.MultipleObjectsReturned:
                raise serializers.ValidationError({'first_manager': BaseMsg.CAUSE_DUPLICATE})
        return None

    second_manager = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_second_manager(cls, value):
        if value:
            try:
                return Employee.objects.get_current(fill__company=True, code=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'second_manager': HRMsg.EMPLOYEE_NOT_EXIST})
            except Employee.MultipleObjectsReturned:
                raise serializers.ValidationError({'second_manager': BaseMsg.CAUSE_DUPLICATE})
        return None

    title = serializers.CharField(max_length=100)

    def create(self, validated_data):
        # get employee list
        group_employee = validated_data.get('group_employee', [])
        group_employee_ids = []
        if group_employee:
            group_employee_ids = [str(item) for item in group_employee.values_list('id', flat=True)]
        validated_data['group_employee'] = group_employee_ids

        # create group
        group = Group.objects.create(**validated_data)

        # force update group of employee
        for obj in group_employee:
            obj.group = group
            obj.save(update_fields=['group'])

        return group

    class Meta:
        model = Group
        fields = (
            'code',
            'group_level',
            'parent_n',
            'title',
            'description',
            'group_employee',
            'first_manager',
            'first_manager_title',
            'second_manager',
            'second_manager_title'
        )


class RoleImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'title', 'code')


class RoleImportSerializer(serializers.ModelSerializer):
    employees = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    @classmethod
    def validate_employees(cls, attrs) -> list:
        if attrs:
            codes = [str(item).strip() for item in list(filter(None, attrs.split(",")))]
            print('codes:', codes)
            objs = Employee.objects.filter_current(code__in=codes, fill__tenant=True, fill__company=True)
            if objs.count() == len(codes):
                return objs
            raise serializers.ValidationError({'employees': HRMsg.EMPLOYEES_NOT_EXIST})
        return []

    @classmethod
    def validate_abbreviation(cls, attrs):
        if Role.objects.filter_current(fill__company=True, abbreviation=attrs).exists():
            raise serializers.ValidationError({'abbreviation': HRMsg.ROLE_CODE_EXIST})
        return attrs

    def create(self, validated_data):
        employees = validated_data.pop('employees', [])
        obj = Role.objects.create(**validated_data)
        if employees:
            RoleHolder.objects.bulk_create(
                [
                    RoleHolder(employee=emp_obj, role=obj)
                    for emp_obj in employees
                ]
            )
        return obj

    class Meta:
        model = Role
        fields = (
            'title',
            'abbreviation',
            'employees',
        )


class EmployeeImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name')


class EmployeeImportSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)

    @classmethod
    def validate_code(cls, value):
        if value:
            if Employee.objects.filter_current(fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": BaseMsg.CODE_IS_EXISTS})
            return value
        raise serializers.ValidationError({"code": BaseMsg.CODE_NOT_NULL})

    user = serializers.CharField(required=False, allow_blank=True)

    @classmethod
    def validate_user(cls, value):
        if value:
            try:
                map_user_employee = CompanyUserEmployee.objects.filter_current(
                    fill__company=True, user__username=value, employee__isnull=True
                )
                if map_user_employee.count() == 1:
                    return map_user_employee.first().user
                raise serializers.ValidationError({
                    'user': HRMsg.USER_RELATE_USED_OR_NOT_FOUND,
                })
            except User.DoesNotExist:
                raise serializers.ValidationError({'user': AccountMsg.USER_NOT_EXIST})
        return None

    group = serializers.CharField(required=False, allow_blank=True)

    @classmethod
    def validate_group(cls, value):
        if value:
            try:
                return Group.objects.get_current(fill__company=True, code=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError({'group': HRMsg.GROUP_NOT_EXIST})
        return None

    role = serializers.CharField(required=False, allow_blank=True)

    @classmethod
    def validate_role(cls, value) -> list:
        if value:
            codes = list(filter(None, [item.strip() for item in value.split(',')]))
            objs = Role.objects.filter_current(fill__company=True, code__in=codes)
            if len(codes) == objs.count():
                return objs
            raise serializers.ValidationError({
                'role': HRMsg.ROLE_CODE_EXIST,
            })
        return []

    date_joined = serializers.DateField(input_formats=['%d/%m/%Y', 'iso-8601'], allow_null=True)
    dob = serializers.DateField(input_formats=['%d/%m/%Y', 'iso-8601'], allow_null=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=25)

    def create(self, validated_data):
        """
            step 1: set up data for create
            step 2: create employee
            step 3: create M2M PlanEmployee + update TenantPlan
            step 4: create M2M Role Employee
        """
        # get role
        role_objs = validated_data.pop('role', [])

        # create new employee
        employee = Employee.objects.create(**validated_data)

        # create M2M Role Employee
        if role_objs:
            RoleHolder.objects.bulk_create(
                RoleHolder(
                    **{
                        'employee': employee,
                        'role_id': role_obj,
                    }
                ) for role_obj in role_objs
            )
        return employee

    class Meta:
        model = Employee
        fields = (
            'code',
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'dob',
            'group',
            'role',
        )
