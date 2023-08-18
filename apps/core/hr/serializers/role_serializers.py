from rest_framework import serializers

from apps.core.hr.models import Role, RoleHolder, PlanRole, Employee
from apps.shared import HRMsg
from apps.shared.permissions import PermissionsUpdateSerializer, PermissionDetailSerializer

from .common import (
    HasPermPlanAppCreateSerializer, HasPermPlanAppUpdateSerializer,
    set_up_data_plan_app, validate_license_used,
    create_plan_role_update_tenant_plan,
)


class RoleListSerializer(serializers.ModelSerializer):
    holder = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'holder',
        )

    @classmethod
    def get_holder(cls, obj):
        return [
            {
                'id': emp['id'],
                'full_name': emp['last_name'] + ' ' + emp['first_name'],
                'code': emp['code'],
            } for emp in obj.employee.all().values('id', 'last_name', 'first_name', 'code')
        ]


class RoleCreateSerializer(serializers.ModelSerializer):
    plan_app = HasPermPlanAppCreateSerializer(many=True)
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    class Meta:
        model = Role
        fields = (
            'title',
            'abbreviation',
            'employees',
            'plan_app',
        )

    @classmethod
    def validate_employees(cls, attrs):
        if attrs and isinstance(attrs, list):
            emp_objs = Employee.objects.filter_current(id__in=attrs, fill__tenant=True, fill__company=True)
            if emp_objs.count() == len(attrs):
                return emp_objs
            raise serializers.ValidationError({'employees': HRMsg.EMPLOYEES_NOT_EXIST})
        return []

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    def create(self, validated_data):
        _plan_application_dict, plan_app_data, bulk_info = set_up_data_plan_app(
            validated_data,
            employee_or_role='role',
        )

        if 'employees' in validated_data:
            employee_objs = validated_data.pop('employees', [])
            role_objs = Role.objects.create(**validated_data)
            if employee_objs:
                holder_bulk_info = [
                    RoleHolder(
                        role=role_objs,
                        employee=employee_obj
                    ) for employee_obj in employee_objs
                ]
                if holder_bulk_info:
                    RoleHolder.objects.bulk_create(holder_bulk_info)

            create_plan_role_update_tenant_plan(
                role=role_objs,
                plan_app_data=plan_app_data,
                bulk_info=bulk_info
            )
            return role_objs
        raise serializers.ValidationError({"detail": HRMsg.ROLE_DATA_VALID})


class RoleUpdateSerializer(PermissionsUpdateSerializer):
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )
    plan_app = HasPermPlanAppUpdateSerializer(
        required=False,
        many=True
    )

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'employees',
            'plan_app',
        )

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    def update(self, instance, validated_data):
        instance, validated_data, _permission_data = self.force_permissions(
            instance=instance, validated_data=validated_data
        )
        plan_application_dict, plan_app_data, bulk_info = set_up_data_plan_app(
            validated_data,
            instance=instance,
            employee_or_role='role',
        )
        if plan_application_dict:
            validated_data.update({'plan_application': plan_application_dict})

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # create M2M PlanEmployee + update TenantPlan
        create_plan_role_update_tenant_plan(
            role=instance,
            plan_app_data=plan_app_data,
            bulk_info=bulk_info
        )

        if 'employees' in validated_data:
            employees_old = RoleHolder.objects.filter(role=instance)
            if employees_old:
                employees_old.delete()
            data_bulk = validated_data.pop('employees')
            if data_bulk:
                bulk_info = []
                for employee in data_bulk:
                    bulk_info.append(
                        RoleHolder(
                            role=instance,
                            employee_id=employee
                        )
                    )
                if bulk_info:
                    RoleHolder.objects.bulk_create(bulk_info)
        return instance


class RoleDetailSerializer(PermissionDetailSerializer):
    cls_of_plan = PlanRole
    cls_key_filter = 'role'

    holder = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'holder',
        )

    @classmethod
    def get_holder(cls, obj):
        result = []
        for emp_obj in obj.employee.all():
            result.append(
                {
                    'id': emp_obj.id,
                    'full_name': emp_obj.get_full_name(),
                    'code': emp_obj.code,
                    'is_active': emp_obj.is_active,
                    'group': {
                        'id': emp_obj.group.id,
                        'title': emp_obj.group.title,
                        'code': emp_obj.group.code,
                    } if emp_obj.group else {},
                }
            )
        return result
