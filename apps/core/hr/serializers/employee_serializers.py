from rest_framework import serializers

from apps.core.account.models import User
from apps.core.hr.models import Employee, PlanEmployee
from apps.core.base.models import SubscriptionPlan, Application


class EmployeePlanAppCreateSerializer(serializers.Serializer):  # noqa
    plan = serializers.UUIDField()
    application = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )

    def validate_plan(self, value):
        try:
            return SubscriptionPlan.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Plan does not exist.")

    def validate_application(self, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            else:
                raise serializers.ValidationError("Some application does not exist.")
        raise serializers.ValidationError("Value must be array.")


class EmployeePlanAppUpdateSerializer(serializers.Serializer):
    plan = serializers.UUIDField(required=False)
    application = serializers.ListSerializer(
        child=serializers.UUIDField(required=False),
        required=False
    )

    def validate_plan(self, value):
        try:
            return SubscriptionPlan.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("Plan does not exist.")

    def validate_application(self, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            else:
                raise serializers.ValidationError("Some application does not exist.")
        raise serializers.ValidationError("Value must be array.")


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

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
            'department',
            'role',
            'is_active',
        )

    def get_full_name(self, obj):
        return Employee.get_full_name(obj, 2)

    def get_date_joined(self, obj):
        return obj.date_created

    def get_department(self, obj):
        return {'id': 1, 'name': 'ABC'}

    def get_role(self, obj):
        return [
            {'id': 1, 'name': 'R1'},
            {'id': 1, 'name': 'R2'},
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

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
        )

    def get_full_name(self, obj):
        return Employee.get_full_name(obj, 2)


class EmployeeCreateSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False)
    plan_app = EmployeePlanAppCreateSerializer(many=True)

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
            'plan_app'
        )

    def validate_user(self, value):
        try:
            return User.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("User does not exist.")

    def create(self, validated_data):
        plan_application_dict = {}
        plan_app_data = None
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
                        bulk_info.append(PlanEmployee(**{
                            'plan': plan_app['plan'],
                            'application': [app.id for app in plan_app['application']]
                        }))
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})
        # create new employee
        employee = Employee.objects.create(**validated_data)
        if employee and plan_app_data and bulk_info:
            # create M2M PlanEmployee
            for info in bulk_info:
                info.employee = employee
            PlanEmployee.object_normal.bulk_create(bulk_info)
        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False)
    plan_app = EmployeePlanAppCreateSerializer(
        required=False,
        many=True
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
            'plan_app'
        )

    def validate_user(self, value):
        try:
            return User.objects.get(id=value)
        except Exception as e:
            raise serializers.ValidationError("User does not exist.")

    def update(self, instance, validated_data):
        plan_application_dict = {}
        plan_app_data = None
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
                        bulk_info.append(PlanEmployee(**{
                            'plan': plan_app['plan'],
                            'application': [app.id for app in plan_app['application']]
                        }))
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})
        # update employee
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if instance and plan_app_data and bulk_info:
            # delete old M2M PlanEmployee
            plan_employee_old = PlanEmployee.object_normal.filter(employee=instance)
            if plan_employee_old:
                plan_employee_old.delete()
            # create M2M PlanEmployee
            for info in bulk_info:
                info.employee = instance
            PlanEmployee.object_normal.bulk_create(bulk_info)
        return instance
