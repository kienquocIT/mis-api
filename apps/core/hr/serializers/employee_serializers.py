from rest_framework import serializers

from apps.core.account.models import User
from apps.core.hr.models import Employee, PlanEmployee, Group, Role, RoleHolder
from apps.core.base.models import SubscriptionPlan, Application, PermissionApplication
from apps.core.tenant.models import TenantPlan
from apps.shared import HRMsg, BaseMsg, AccountMsg, PERMISSION_OPTION


class EmployeePlanAppCreateSerializer(serializers.Serializer):  # noqa
    plan = serializers.UUIDField()
    application = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    license_used = serializers.IntegerField(required=False)
    license_quantity = serializers.IntegerField(required=False)

    @classmethod
    def validate_plan(cls, value):
        try:
            return SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist as exc:
            raise serializers.ValidationError(BaseMsg.PLAN_NOT_EXIST) from exc

    @classmethod
    def validate_application(cls, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            raise serializers.ValidationError(BaseMsg.APPLICATIONS_NOT_EXIST)
        raise serializers.ValidationError(BaseMsg.APPLICATION_IS_ARRAY)


class EmployeePlanAppUpdateSerializer(serializers.Serializer):  # noqa
    plan = serializers.UUIDField(required=False)
    application = serializers.ListSerializer(
        child=serializers.UUIDField(required=False),
        required=False
    )
    license_used = serializers.IntegerField(required=False)
    license_quantity = serializers.IntegerField(required=False)

    @classmethod
    def validate_plan(cls, value):
        try:
            return SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist as exc:
            raise serializers.ValidationError(BaseMsg.PLAN_NOT_EXIST) from exc

    @classmethod
    def validate_application(cls, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            raise serializers.ValidationError(BaseMsg.APPLICATIONS_NOT_EXIST)
        raise serializers.ValidationError(BaseMsg.APPLICATION_IS_ARRAY)


class RoleOfEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'title', 'code')


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


class EmployeeListMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'code',
            'first_name',
            'last_name',
            'full_name',
        )

    def get_full_name(self, obj):
        return obj.get_full_name(2)


class EmployeeDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    plan_app = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    permission_by_configured = serializers.JSONField()

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
            'permission_by_configured',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name(2)

    @classmethod
    def get_plan_app(cls, obj):
        result = []
        employee_plan = PlanEmployee.objects.select_related('plan').filter(
            employee=obj
        )
        if employee_plan:
            for emp_plan in employee_plan:
                app_list = []
                if emp_plan.application and isinstance(emp_plan.application, list):
                    application_list = Application.objects.filter(
                        id__in=emp_plan.application
                    ).values('id', 'title', 'code')
                    if application_list:
                        for application in application_list:
                            app_list.append(
                                {
                                    'id': application['id'],
                                    'title': application['title'],
                                    'code': application['code']
                                }
                            )
                result.append(
                    {
                        'id': emp_plan.plan_id,
                        'title': emp_plan.plan.title,
                        'code': emp_plan.plan.code,
                        'application': app_list
                    }
                )
        return result

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
def validate_employee_create_update(validate_data):
    plan_license_check = ""
    if 'user' in validate_data:
        if 'plan_app' in validate_data:
            for plan_app in validate_data['plan_app']:
                if 'plan' in plan_app and 'license_used' in plan_app and 'license_quantity' in plan_app:
                    if plan_app['license_used'] > plan_app['license_quantity']:
                        plan_license_check += plan_app['plan'].title + ", "
    if plan_license_check:
        raise serializers.ValidationError(
            {
                'detail': HRMsg.EMPLOYEE_PLAN_APP_CHECK.format(plan_license_check)
            }
        )
    return validate_data


def set_up_data_plan_app(validated_data):
    plan_application_dict = {}
    plan_app_data = []
    bulk_info = []
    if 'plan_app' in validated_data:
        plan_app_data = validated_data['plan_app']
        del validated_data['plan_app']
    if plan_app_data:
        for plan_app in plan_app_data:
            plan_code = None
            app_code_list = []
            if 'plan' in plan_app:
                plan_code = plan_app['plan'].code if plan_app['plan'] else None
            if 'application' in plan_app:
                app_code_list = [app.code for app in plan_app['application']] if plan_app['application'] else []
            if plan_code and app_code_list:
                plan_application_dict.update({plan_code: app_code_list})
                bulk_info.append(
                    PlanEmployee(
                        **{
                            'plan': plan_app['plan'],
                            'application': [app.id for app in plan_app['application']]
                        }
                    )
                )
    return plan_application_dict, plan_app_data, bulk_info


def create_plan_employee_update_tenant_plan(
        employee,
        plan_app_data,
        bulk_info
):
    if employee and plan_app_data and bulk_info:
        # create M2M PlanEmployee
        for info in bulk_info:
            info.employee = employee
        PlanEmployee.objects.bulk_create(bulk_info)
        # update TenantPlan
        for plan_data in plan_app_data:
            if 'plan' in plan_data and 'license_used' in plan_data:
                tenant_plan = TenantPlan.objects.filter(
                    tenant=employee.tenant,
                    plan=plan_data['plan']
                ).first()
                if tenant_plan:
                    tenant_plan.license_used = plan_data['license_used']
                    tenant_plan.save()
    return True


def validate_role_for_employee(value):
    if value and isinstance(value, list):
        role_list = Role.objects.filter(id__in=value).count()
        if role_list == len(value):
            return value
        raise serializers.ValidationError({'detail': HRMsg.ROLES_NOT_EXIST})
    raise serializers.ValidationError({'detail': HRMsg.ROLE_IS_ARRAY})


class EmployeeCreateSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False)
    plan_app = EmployeePlanAppCreateSerializer(many=True)
    group = serializers.UUIDField(required=False)
    role = serializers.ListField(child=serializers.UUIDField(required=False), required=False)

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
        )

    @classmethod
    def validate_user(cls, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({'detail': AccountMsg.USER_NOT_EXIST}) from exc

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
        return validate_employee_create_update(validate_data=validate_data)

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


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False)
    plan_app = EmployeePlanAppUpdateSerializer(
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

    permission_by_configured = serializers.JSONField(
        required=False,
        help_text=str(Employee.permission_by_configured_sample)
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
            'permission_by_configured',
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
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': AccountMsg.USER_NOT_EXIST})

    def validate(self, validate_data):
        return validate_employee_create_update(validate_data=validate_data)

    def update(self, instance, validated_data):
        """
            step 1: set up data for update
            step 2: update employee
            step 3: delete old M2M PlanEmployee + create new M2M PlanEmployee + update TenantPlan
            step 4: delete old M2M RoleEmployee + create new M2M RoleEmployee
        """
        plan_application_dict, plan_app_data, bulk_info = set_up_data_plan_app(validated_data)
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})

        role_list = None
        if 'role' in validated_data:
            role_list = validated_data['role']
            del validated_data['role']

        # update employee
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if 'permission_by_configured' in validated_data.keys():
            instance.save_permissions(field_name=['permission_by_configured'])

        # delete old M2M PlanEmployee
        plan_employee_old = PlanEmployee.objects.filter(employee=instance)
        if plan_employee_old:
            plan_employee_old.delete()

        # create M2M PlanEmployee + update TenantPlan
        create_plan_employee_update_tenant_plan(
            employee=instance,
            plan_app_data=plan_app_data,
            bulk_info=bulk_info
        )

        # delete old M2M RoleEmployee
        role_employee_old = RoleHolder.objects.filter(employee=instance)
        if role_employee_old:
            role_employee_old.delete()

        # create M2M RoleEmployee
        if instance and role_list:
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

    @classmethod
    def validate_permission_by_configured(cls, attrs):
        """
        Permissions By Configured format should a dictionary:
            key: '{code}__{app_label}__{model}'
            value: {'option': PERMISSION_OPTION}

        Code_name in models PermissionApplication (cached 14 days)
        Config_data must be required "option" name key and value exist in PERMISSION_OPTION.
        """
        if isinstance(attrs, dict):
            option_choices = [x[0] for x in PERMISSION_OPTION]
            permission_choices = {x.permission: x for x in PermissionApplication.objects.all()}
            for code_name, config_data in attrs.items():
                # check code_name exist
                if not (code_name and code_name in permission_choices):
                    raise serializers.ValidationError(HRMsg.PERMISSIONS_BY_CONFIGURED_INCORRECT)

                # check config_data
                if config_data and isinstance(config_data, dict) and 'option' in config_data:
                    option = config_data['option']
                    if option not in option_choices:
                        raise serializers.ValidationError(HRMsg.PERMISSIONS_BY_CONFIGURED_CHILD_INCORRECT)
                else:
                    raise serializers.ValidationError(HRMsg.PERMISSIONS_BY_CONFIGURED_CHILD_INCORRECT)
            return attrs
        raise serializers.ValidationError(HRMsg.PERMISSIONS_BY_CONFIGURED_INCORRECT)
