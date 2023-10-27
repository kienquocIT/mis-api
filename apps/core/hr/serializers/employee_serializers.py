from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.account.models import User
from apps.core.hr.models import Employee, PlanEmployee, Group, Role, RoleHolder, EmployeePermission, PlanEmployeeApp
from apps.shared import HRMsg, AccountMsg, AttMsg, TypeCheck, call_task_background
from apps.shared.permissions.util import PermissionController
from apps.eoffice.leave.leave_util import leave_available_map_employee as available_map_employee

from .common import (
    HasPermPlanAppCreateSerializer,
    set_up_data_plan_app, validate_license_used,
    create_plan_employee_update_tenant_plan, PlanAppUpdateSerializer,
)
from ..tasks import sync_plan_app_employee
from ...base.models import Application, PlanApplication
from ...tenant.models import TenantPlan


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


class EmployeeDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    permission_by_configured = serializers.SerializerMethodField()
    plan_app = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id', 'code', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'plan_app', 'user',
            'group', 'dob', 'date_joined', 'role', 'is_admin_company', 'is_active',
            'permission_by_configured', 'plan_app',
        )

    @classmethod
    def get_permission_by_configured(cls, obj):
        return EmployeePermission.objects.get(employee=obj).permission_by_configured

    @classmethod
    def get_plan_app(cls, obj):
        result = []
        for obj_plan_employee in PlanEmployee.objects.filter(employee=obj).select_related('plan').prefetch_related(
                'application_m2m'
        ):
            item_data = {
                'id': obj_plan_employee.plan_id,
                'title': obj_plan_employee.plan.title,
                'code': obj_plan_employee.plan.code,
                'application': []
            }
            for obj_app in obj_plan_employee.application_m2m.all():
                item_data['application'].append(
                    {
                        'id': obj_app.id,
                        'title': obj_app.title,
                        'code': obj_app.code,
                        'model_code': obj_app.model_code,
                        'app_label': obj_app.app_label,
                        'option_permission': obj_app.option_permission,
                        'option_allowed': obj_app.option_allowed,
                        'permit_mapping': obj_app.permit_mapping,
                    }
                )
            result.append(item_data)
        return result

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


class ApplicationOfEmployeeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    @classmethod
    def get_id(cls, obj):
        return obj.application.id

    title = serializers.SerializerMethodField()

    @classmethod
    def get_title(cls, obj):
        return obj.application.title

    code = serializers.SerializerMethodField()

    @classmethod
    def get_code(cls, obj):
        return obj.application.code

    permit_mapping = serializers.SerializerMethodField()

    @classmethod
    def get_permit_mapping(cls, obj):
        return obj.application.permit_mapping

    class Meta:
        model = PlanEmployeeApp
        fields = ('id', 'title', 'code', 'permit_mapping')


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
        if value is not None:
            try:
                return Group.objects.get(id=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError({'detail': HRMsg.GROUP_NOT_EXIST})
        return None

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

        # create new leave available list for employee
        available_map_employee(employee, self.context.get('company_obj', None))
        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False, allow_null=True)
    group = serializers.UUIDField(required=False, allow_null=True)
    role = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    email = serializers.CharField(max_length=150, required=False)
    phone = serializers.CharField(max_length=25, required=False)
    plan_app = PlanAppUpdateSerializer(required=False, many=True)
    permission_by_configured = serializers.JSONField(required=False)

    class Meta:
        model = Employee
        fields = (
            'user', 'first_name', 'last_name', 'email', 'phone', 'date_joined', 'dob',
            'group', 'role', 'is_admin_company',
            'plan_app', 'permission_by_configured',
        )

    @classmethod
    def reset_plan_app_employee(cls, employee_obj):
        obj = PlanEmployeeApp.objects.filter(plan_employee__employee=employee_obj)
        if obj:
            obj.delete()
        obj2 = PlanEmployee.objects.filter(employee=employee_obj)
        if obj2:
            obj2.delete()
        return True

    @classmethod
    def force_permissions(cls, instance, validated_data, emp_need_sync: list[str] = None):
        plan_app = validated_data.pop('plan_app', None)
        if isinstance(plan_app, dict):
            # plan_app: {"plan_id": ["app_id"]}
            cls.reset_plan_app_employee(employee_obj=instance)
            if plan_app:
                for plan_id, app_ids in plan_app.items():
                    plan_employee_obj = PlanEmployee.objects.create(employee=instance, plan_id=plan_id)
                    for app_id in app_ids:
                        PlanEmployeeApp.objects.get_or_create(plan_employee=plan_employee_obj, application_id=app_id)

        if emp_need_sync and isinstance(emp_need_sync, list):
            call_task_background(
                sync_plan_app_employee,
                **{
                    'employee_ids': emp_need_sync,
                },
            )

        permissions_data = validated_data.pop('permission_by_configured', None)
        if permissions_data is not None and isinstance(permissions_data, list):
            setattr(instance, 'permission_by_configured', permissions_data)

            emp_permit, _created = EmployeePermission.objects.get_or_create(employee=instance)
            emp_permit.permission_by_configured = permissions_data
            permissions_parsed = PermissionController(
                tenant_id=instance.tenant_id
            ).get_permission_parsed(
                instance=emp_permit
            )
            setattr(emp_permit, 'permissions_parsed', permissions_parsed)
            emp_permit.save()

            setattr(instance, 'permissions_parsed', permissions_parsed)
        return instance, validated_data, permissions_data

    def validate_permission_by_configured(self, attrs):
        return PermissionController(tenant_id=self.instance.tenant_id).valid(attrs=attrs)

    def validate_plan_app(self, attrs):
        if isinstance(attrs, list):
            plan_ids = []
            app_ids = []
            app_by_plan = {}
            for item in attrs:
                if 'plan' in item and item['plan'] and TypeCheck.check_uuid(item['plan']):
                    item_plan = str(item['plan'])
                    plan_ids.append(item_plan)
                    application_data = [str(ite) for ite in item.get('application', [])]
                    app_ids += application_data
                    app_by_plan[item_plan] = application_data
                else:
                    raise serializers.ValidationError({'plan_app': HRMsg.PLAN_NOT_FOUND})

            plan_ids = list(set(plan_ids))
            plan_check = TenantPlan.objects.filter(tenant_id=self.instance.tenant_id, plan_id__in=plan_ids)
            if len(plan_ids) != plan_check.count():
                raise serializers.ValidationError({'plan_app': HRMsg.PLAN_NOT_FOUND})

            app_ids = list(set(app_ids))
            app_check = Application.objects.filter(id__in=app_ids)
            if len(app_ids) != app_check.count():
                raise serializers.ValidationError({'plan_app': HRMsg.APP_NOT_FOUND})

            for obj in plan_check:
                application_data = app_by_plan[str(obj.plan_id)]
                if application_data and TypeCheck.check_uuid_list(application_data):
                    objs_tmp = PlanApplication.objects.filter(plan_id=obj.plan_id, application_id__in=application_data)
                    if objs_tmp.count() != len(application_data):
                        raise serializers.ValidationError({'plan_app': HRMsg.APP_NOT_MATCH_PLAN})
            return app_by_plan

        raise serializers.ValidationError({'plan_app': HRMsg.PLAN_TYPE_INCORRECT})

    @classmethod
    def validate_group(cls, value):
        if value is not None:
            try:
                return Group.objects.get(id=value)
            except Group.DoesNotExist:
                raise serializers.ValidationError({'detail': HRMsg.GROUP_NOT_EXIST})
        return None

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

    @classmethod
    def destroy_and_recreate_role_holder(cls, instance, validated_data):
        if 'role' in validated_data:
            role_list = validated_data['role']
            del validated_data['role']

            # delete old M2M RoleEmployee
            role_employee_old = RoleHolder.objects.filter(employee=instance)
            if role_employee_old:
                role_employee_old.delete()

            # create M2M RoleEmployee | !!! update member before force sync employee plan-app-permission
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
        return validated_data

    def update(self, instance, validated_data):
        """
            step 1: delete old M2M PlanEmployee + create new M2M PlanEmployee + update TenantPlan
            step 2: delete old M2M RoleEmployee + create new M2M RoleEmployee
            step 3: set up data for update
            step 4: update employee
        """
        self.destroy_and_recreate_role_holder(instance=instance, validated_data=validated_data)

        instance, validated_data, _permission_data = self.force_permissions(
            instance=instance, validated_data=validated_data, emp_need_sync=[str(instance.id)]
        )

        # update employee
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
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
