from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.account.models import User
from apps.core.hr.models import Employee, PlanEmployee, Group, Role, RoleHolder
from apps.shared import HRMsg, AccountMsg, AttMsg
from apps.shared.permissions import PermissionDetailSerializer, PermissionsUpdateSerializer

from .common import (
    HasPermPlanAppCreateSerializer, HasPermPlanAppUpdateSerializer,
    set_up_data_plan_app, validate_license_used,
    create_plan_employee_update_tenant_plan,
)


class RoleOfEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'title', 'code')


class EmployeeUploadAvatarSerializer(serializers.Serializer):  # noqa
    file = serializers.FileField()

    @classmethod
    def validate_file(cls, value):
        max_size = settings.AVATAR_FILE_MAX_SIZE
        if value.size > max_size:
            raise ValidationError({'file': AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format('5MiB')})

        file_name = value.name
        if file_name.split('.')[-1].lower() not in ['jpeg', 'jpg', 'png', 'gif']:
            raise ValidationError(
                {'file': AttMsg.IMAGE_TYPE_SHOULD_BE_IMAGE_TYPE.format(", ".join(['jpeg', 'jpg', 'png', 'gif']))}
            )

        return value


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_ids = []

    class Meta:
        model = Employee
        fields = (
            'id',
            'code',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'date_joined',
            'role',
            'is_active',
            'group',
            'role',
            'is_admin_company',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name(2)

    @classmethod
    def get_group(cls, obj):
        if obj.group_id:
            return {
                'id': obj.group_id,
                'title': obj.group.title,
                'code': obj.group.code
            }
        return {}

    @classmethod
    def get_role(cls, obj):
        return [
            {
                'id': x.id,
                'title': x.title,
                'code': x.code,
            } for x in obj.role.all()
        ]


class EmployeeDetailSerializer(PermissionDetailSerializer):
    cls_of_plan = PlanEmployee
    cls_key_filter = 'employee'

    full_name = serializers.SerializerMethodField()
    plan_app = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'code',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'plan_app',
            'user',
            'group',
            'dob',
            'date_joined',
            'role',
            'is_admin_company',
            'is_active',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name(2)

    @classmethod
    def get_user(cls, obj):
        if obj.user:
            return {
                'id': obj.user_id,
                'full_name': obj.user.get_full_name(2),
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'email': obj.user.email,
                'phone': obj.user.phone,
            }
        return {}

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            return {
                'id': obj.group_id,
                'title': obj.group.title,
                'code': obj.group.code
            }
        return {}

    @classmethod
    def get_role(cls, obj):
        result = []
        role_list = obj.role.all().values(
            'id',
            'title'
        )
        if role_list:
            for role in role_list:
                result.append(
                    {
                        'id': role['id'],
                        'title': role['title'],
                    }
                )
        return result


# functions for create/ update employee

def validate_role_for_employee(value):
    if isinstance(value, list):
        if value:
            role_list = Role.objects.filter(id__in=value).count()
            if role_list == len(value):
                return value
            raise serializers.ValidationError({'detail': HRMsg.ROLES_NOT_EXIST})
        return value
    raise serializers.ValidationError({'detail': HRMsg.ROLE_IS_ARRAY})


class EmployeeCreateSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False)
    plan_app = HasPermPlanAppCreateSerializer(many=True)
    group = serializers.UUIDField(required=False, allow_null=True)
    role = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=25)

    class Meta:
        model = Employee
        fields = (
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'dob',
            'plan_app',
            'group',
            'role',
            'is_admin_company',
        )

    @classmethod
    def validate_user(cls, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': AccountMsg.USER_NOT_EXIST})

    @classmethod
    def validate_group(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.GROUP_NOT_EXIST})

    @classmethod
    def validate_role(cls, value):
        return validate_role_for_employee(value)

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    def create(self, validated_data):
        """
            step 1: set up data for create
            step 2: create employee
            step 3: create M2M PlanEmployee + update TenantPlan
            step 4: create M2M Role Employee
        """
        plan_application_dict, plan_app_data, bulk_info = set_up_data_plan_app(validated_data)
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})

        role_list = None
        if 'role' in validated_data:
            role_list = validated_data['role']
            del validated_data['role']

        # create new employee
        employee = Employee.objects.create(**validated_data)

        # create M2M PlanEmployee + update TenantPlan
        create_plan_employee_update_tenant_plan(
            employee=employee,
            plan_app_data=plan_app_data,
            bulk_info=bulk_info
        )

        # create M2M Role Employee
        if role_list:
            bulk_info = []
            for role in role_list:
                bulk_info.append(
                    RoleHolder(
                        **{
                            'employee': employee,
                            'role_id': role,
                        }
                    )
                )
            RoleHolder.objects.bulk_create(bulk_info)
        return employee


class EmployeeUpdateSerializer(PermissionsUpdateSerializer):
    user = serializers.UUIDField(required=False, allow_null=True)
    plan_app = HasPermPlanAppUpdateSerializer(
        required=False,
        many=True
    )
    group = serializers.UUIDField(required=False)
    role = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    first_name = serializers.CharField(
        max_length=100,
        required=False
    )
    last_name = serializers.CharField(
        max_length=100,
        required=False
    )
    email = serializers.CharField(
        max_length=150,
        required=False
    )
    phone = serializers.CharField(
        max_length=25,
        required=False
    )

    class Meta:
        model = Employee
        fields = (
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'dob',
            'plan_app',
            'group',
            'role',
            'is_admin_company',
        )

    @classmethod
    def validate_group(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.GROUP_NOT_EXIST})

    @classmethod
    def validate_role(cls, value):
        return validate_role_for_employee(value)

    @classmethod
    def validate_user(cls, value):
        if value is not None:
            try:
                return User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError({'detail': AccountMsg.USER_NOT_EXIST})
        return None

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    def update(self, instance, validated_data):
        """
            step 1: set up data for update
            step 2: update employee
            step 3: delete old M2M PlanEmployee + create new M2M PlanEmployee + update TenantPlan
            step 4: delete old M2M RoleEmployee + create new M2M RoleEmployee
        """
        instance, validated_data, _permission_data = self.force_permissions(
            instance=instance, validated_data=validated_data
        )

        plan_application_dict, plan_app_data, bulk_info = set_up_data_plan_app(
            validated_data,
            instance=instance
        )
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})

        role_list = []
        if 'role' in validated_data:
            role_list = validated_data['role']
            del validated_data['role']
            # delete old M2M RoleEmployee
            role_employee_old = RoleHolder.objects.filter(employee=instance)
            if role_employee_old:
                role_employee_old.delete()

        # update employee
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # create M2M PlanEmployee + update TenantPlan
        create_plan_employee_update_tenant_plan(
            employee=instance,
            plan_app_data=plan_app_data,
            bulk_info=bulk_info
        )

        # create M2M RoleEmployee
        if role_list:
            bulk_info = []
            for role in role_list:
                bulk_info.append(
                    RoleHolder(
                        **{
                            'employee': instance,
                            'role_id': role,
                        }
                    )
                )
            RoleHolder.objects.bulk_create(bulk_info)

        return instance


# EMPLOYEE by overview Tenant
class EmployeeListByOverviewTenantSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    license = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'code',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'date_joined',
            'is_active',
            'user',
            'license',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name(2)

    @classmethod
    def get_user(cls, obj):
        if obj.user_id:
            return {
                'id': str(obj.user_id),
                'first_name': str(obj.user.first_name),
                'last_name': str(obj.user.last_name),
                'full_name': str(obj.user.get_full_name())
            }
        return {}

    @classmethod
    def get_license(cls, obj):
        return [
            {
                'id': x.id,
                'title': x.title,
                'code': x.code
            } for x in obj.plan.all()
        ]


class EmployeeListMinimalByOverviewTenantSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    is_linked_user = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'code',
            'first_name',
            'last_name',
            'full_name',
            'is_linked_user',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name(2)

    @classmethod
    def get_is_linked_user(cls, obj):
        if obj.user_id:
            return True
        return False
