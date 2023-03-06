from rest_framework import serializers

from apps.core.account.models import User
from apps.core.hr.models import Employee, PlanEmployee, Group, Role, RoleHolder
from apps.core.base.models import SubscriptionPlan, Application
from apps.core.tenant.models import TenantPlan
from apps.shared import HrMsg, PERMISSION_OPTION


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
            raise serializers.ValidationError("Plan does not exist.") from exc

    @classmethod
    def validate_application(cls, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            raise serializers.ValidationError("Some application does not exist.")
        raise serializers.ValidationError("Value must be array.")


class EmployeePlanAppUpdateSerializer(serializers.Serializer): # noqa
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
            raise serializers.ValidationError("Plan does not exist.") from exc

    @classmethod
    def validate_application(cls, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            raise serializers.ValidationError("Some application does not exist.")
        raise serializers.ValidationError("Value must be array.")


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

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
            'user'
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name(2)

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
            'title',
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

    @classmethod
    def get_user(cls, obj):
        if obj.user:
            return {
                'id': obj.user_id,
                'username': obj.user.username,
            }
        return {}


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
        employee_plan = PlanEmployee.object_normal.select_related('plan').filter(
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
            raise serializers.ValidationError("User does not exist.") from exc

    @classmethod
    def validate_group(cls, value):
        try:
            return Group.object_global.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist.")

    @classmethod
    def validate_role(cls, value):
        if isinstance(value, list):
            role_list = Role.object_global.filter(id__in=value).count()
            if role_list == len(value):
                return value
            raise serializers.ValidationError("Some role does not exist.")
        raise serializers.ValidationError("Role must be array.")

    def validate(self, validate_data):
        plan_license_check = ""
        if 'user' in validate_data:
            if 'plan_app' in validate_data:
                for plan_app in validate_data['plan_app']:
                    if 'plan' in plan_app and 'license_used' in plan_app and 'license_quantity' in plan_app:
                        if plan_app['license_used'] > plan_app['license_quantity']:
                            plan_license_check += plan_app['plan'].title + ", "
        if plan_license_check:
            raise serializers.ValidationError(HrMsg.LICENSE_OVER_TOTAL.format(str(plan_license_check)))
        return validate_data

    def create(self, validated_data):   # pylint: disable=R0912
        """
        Steps:
            1. Create plan app (function: create_plan_app)
            2. Create user

        """
        plan_application_dict = {}
        plan_app_data = None
        role_list = None
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
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})
        if 'role' in validated_data:
            role_list = validated_data['role']
            del validated_data['role']
        # create new employee
        employee = Employee.objects.create(**validated_data)
        # create M2M PlanEmployee + update TenantPlan
        if employee and plan_app_data and bulk_info:
            # create M2M PlanEmployee
            for info in bulk_info:
                info.employee = employee
            PlanEmployee.object_normal.bulk_create(bulk_info)
            # update TenantPlan
            for plan_data in plan_app_data:
                if 'plan' in plan_data and 'license_used' in plan_data:
                    tenant_plan = TenantPlan.object_normal.filter(
                        tenant=employee.tenant,
                        plan=plan_data['plan']
                    ).first()
                    if tenant_plan:
                        tenant_plan.license_used = plan_data['license_used']
                        tenant_plan.save()
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
            RoleHolder.object_normal.bulk_create(bulk_info)
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
            return Group.object_global.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist.")

    @classmethod
    def validate_role(cls, value):
        if isinstance(value, list):
            role_list = Role.object_global.filter(id__in=value).count()
            if role_list == len(value):
                return value
            raise serializers.ValidationError("Some role does not exist.")
        raise serializers.ValidationError("Role must be array.")

    @classmethod
    def validate_user(cls, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

    def validate(self, validate_data):
        plan_license_check = ""
        if 'user' in validate_data:
            if 'plan_app' in validate_data:
                for plan_app in validate_data['plan_app']:
                    if 'plan' in plan_app and 'license_used' in plan_app and 'license_quantity' in plan_app:
                        if plan_app['license_used'] > plan_app['license_quantity']:
                            plan_license_check += plan_app['plan'].title + ", "
        if plan_license_check:
            raise serializers.ValidationError(
                "Licenses used of " + plan_license_check + "plan is over total licenses."
            )
        return validate_data

    def update(self, instance, validated_data): # pylint: disable=R0912,R0914
        plan_application_dict = {}
        plan_app_data = None
        role_list = None
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
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})
        if 'role' in validated_data:
            role_list = validated_data['role']
            del validated_data['role']
        # update employee
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # delete old M2M PlanEmployee
        plan_employee_old = PlanEmployee.object_normal.filter(employee=instance)
        if plan_employee_old:
            plan_employee_old.delete()
        # create M2M PlanEmployee + update TenantPlan
        if instance and plan_app_data and bulk_info:
            # create M2M PlanEmployee
            for info in bulk_info:
                info.employee = instance
            PlanEmployee.object_normal.bulk_create(bulk_info)
            # update TenantPlan
            for plan_data in plan_app_data:
                if 'plan' in plan_data and 'license_used' in plan_data:
                    tenant_plan = TenantPlan.object_normal.filter(
                        tenant=instance.tenant,
                        plan=plan_data['plan']
                    ).first()
                    if tenant_plan:
                        tenant_plan.license_used = plan_data['license_used']
                        tenant_plan.save()

        # delete old M2M RoleEmployee
        role_employee_old = RoleHolder.object_normal.filter(employee=instance)
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
            RoleHolder.object_normal.bulk_create(bulk_info)

        return instance

    @classmethod
    def validate_permission_by_configured(cls, attrs):
        if isinstance(attrs, dict):
            option_choices = [x[0] for x in PERMISSION_OPTION]
            for code_name, config_data in attrs.items():
                # check code_name exist
                if code_name:
                    ...

                # check config_data
                if config_data and isinstance(config_data, dict) and 'option' in config_data:
                    option = config_data['option']
                    if option not in option_choices:
                        raise serializers.ValidationError(HrMsg.PERMISSIONS_BY_CONFIGURED_OPTION_INCORRECT)
                else:
                    raise serializers.ValidationError(HrMsg.PERMISSIONS_BY_CONFIGURED_CHILD_REQUIRED)
        raise serializers.ValidationError(HrMsg.PERMISSIONS_BY_CONFIGURED_DICT_TYPE)
