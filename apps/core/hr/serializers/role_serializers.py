from rest_framework import serializers

from apps.core.hr.models import Role, RoleHolder, PlanRole
from apps.core.hr.serializers.plan_app_serializers import PlanAppSerializer
from apps.shared import HRMsg, HttpMsg

from apps.core.tenant.utils import PlanController


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
        )

    def create(self, validated_data):
        if 'employees' in validated_data:
            data_bulk = validated_data.pop('employees')
            role = Role.objects.create(**validated_data)
            if data_bulk:
                bulk_info = []
                for employee in data_bulk:
                    bulk_info.append(
                        RoleHolder(
                            role=role,
                            employee_id=employee
                        )
                    )
                if bulk_info:
                    RoleHolder.objects.bulk_create(bulk_info)
            return role
        raise serializers.ValidationError({"detail": HRMsg.ROLE_DATA_VALID})


class RoleUpdateSerializer(serializers.ModelSerializer):
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )
    plan_app = PlanAppSerializer(many=True, required=False)

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'employees',
            'plan_app',
        )

    def validate_plan_app(self, attrs):
        ser = PlanAppSerializer(data=attrs, many=True)
        ser.is_valid(raise_exception=True)

        app_ids = []
        plan_ids = [str(x) for x in PlanController.get_plan_of_tenant(tenant_id=self.instance.tenant_id)]
        if plan_ids:
            for item in ser.validated_data:
                plan = item['plan']
                app_ids += item['application']
                if str(plan) not in plan_ids:
                    raise serializers.ValidationError({'plan_app': HttpMsg.PLAN_DENY_PERMIT})
            if len(app_ids) == len(PlanController.get_app(app_ids)):
                return attrs
            raise serializers.ValidationError({'plan_app': HttpMsg.APP_DENY_PERMIT})
        return []

    def update(self, instance, validated_data):
        plan_app = validated_data.pop('plan_app', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if plan_app:
            new_data = PlanAppSerializer.convert_to_simple(plan_app)
            instance.sync_plan_app(new_data)

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
        raise serializers.ValidationError({"detail": HRMsg.ROLE_DATA_VALID})


class RoleDetailSerializer(serializers.ModelSerializer):
    holder = serializers.SerializerMethodField()
    plan_app = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'title',
            'abbreviation',
            'holder',
            'plan_app',
        )

    @classmethod
    def get_plan_app(cls, obj):
        result = []
        role_plan_arr = PlanRole.objects.select_related('plan').prefetch_related('application_m2m').filter(role=obj)
        if role_plan_arr:
            for role_plan in role_plan_arr:
                tmp = {
                    'id': role_plan.plan_id,
                    'title': role_plan.plan.title,
                    'code': role_plan.plan.code,
                    'application': []
                }
                for app_obj in role_plan.application_m2m.all():
                    tmp['application'].append(
                        {
                            'id': app_obj.id,
                            'title': app_obj.title,
                            'code': app_obj.code,
                            'app_label': app_obj.app_label,
                            'option_permission': app_obj.option_permission,
                            'range_allow': app_obj.get_range_allow(app_obj.option_permission),
                        }
                    )
                result.append(tmp)
        return result

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
