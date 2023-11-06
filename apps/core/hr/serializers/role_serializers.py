from rest_framework import serializers

from apps.core.base.models import Application, PlanApplication
from apps.core.tenant.models import TenantPlan

from apps.core.hr.models import Role, RoleHolder, PlanRole, Employee, RolePermission, PlanRoleApp
from apps.core.hr.tasks import sync_plan_app_employee

from apps.shared import HRMsg, TypeCheck, call_task_background
from apps.shared.permissions.util import PermissionController

from .common import (
    HasPermPlanAppCreateSerializer,
    set_up_data_plan_app, validate_license_used,
    create_plan_role_update_tenant_plan, PlanAppUpdateSerializer,
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


class RoleUpdateSerializer(serializers.ModelSerializer):
    employees = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )
    plan_app = PlanAppUpdateSerializer(required=False, many=True)
    permission_by_configured = serializers.JSONField(required=False)

    class Meta:
        model = Role
        fields = (
            'id', 'title', 'abbreviation', 'employees', 'plan_app',
            'plan_app', 'permission_by_configured',
        )

    @classmethod
    def reset_plan_app_role(cls, role_obj):
        obj = PlanRoleApp.objects.filter(plan_role__role=role_obj)
        if obj:
            obj.delete()
        obj2 = PlanRole.objects.filter(role=role_obj)
        if obj2:
            obj2.delete()
        return True

    @classmethod
    def force_permissions(cls, instance, validated_data, emp_need_sync: list[str] = None):
        plan_app = validated_data.pop('plan_app', None)
        if isinstance(plan_app, dict):
            # plan_app: {"plan_id": ["app_id"]}
            cls.reset_plan_app_role(role_obj=instance)
            if plan_app:
                for plan_id, app_ids in plan_app.items():
                    plan_role_obj = PlanRole.objects.create(role=instance, plan_id=plan_id)
                    for app_id in app_ids:
                        PlanRoleApp.objects.get_or_create(plan_role=plan_role_obj, application_id=app_id)
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

            role_permit, _created = RolePermission.objects.get_or_create(role=instance)
            role_permit.permission_by_configured = permissions_data
            permissions_parsed = PermissionController(
                tenant_id=instance.tenant_id
            ).get_permission_parsed(
                instance=role_permit
            )
            setattr(role_permit, 'permissions_parsed', permissions_parsed)
            role_permit.save()

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

    def validate(self, validate_data):
        return validate_license_used(validate_data=validate_data)

    @classmethod
    def validate_employees(cls, attrs):
        objs = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=attrs)
        if len(attrs) == objs.count():
            return [str(ite) for ite in attrs]
        raise serializers.ValidationError({'employee': HRMsg.MEMBER_NOT_FOUND})

    @classmethod
    def destroy_and_recreate_holder(cls, instance, validated_data):
        emp_need_sync = []
        if 'employees' in validated_data:
            old_holders = RoleHolder.objects.filter(role=instance)
            new_member_ids = validated_data.pop('employees', [])
            emp_need_sync = list(set([str(obj.employee_id) for obj in old_holders] + new_member_ids))
            # destroy holder was removed from user
            if old_holders:
                old_holders.delete()
            # recreate holder
            RoleHolder.objects.bulk_create(
                [
                    RoleHolder(
                        role=instance,
                        employee_id=emp_id,
                    ) for emp_id in new_member_ids
                ]
            )
        return emp_need_sync

    def update(self, instance, validated_data):
        emp_need_sync = self.destroy_and_recreate_holder(instance=instance, validated_data=validated_data)
        instance, validated_data, _permission_data = self.force_permissions(
            instance=instance, validated_data=validated_data, emp_need_sync=emp_need_sync,
        )

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class RoleDetailSerializer(serializers.ModelSerializer):
    holder = serializers.SerializerMethodField()
    permission_by_configured = serializers.SerializerMethodField()
    plan_app = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id', 'title', 'abbreviation', 'holder',
            'permission_by_configured', 'plan_app',
        )

    @classmethod
    def get_permission_by_configured(cls, obj):
        return RolePermission.objects.get(role=obj).permission_by_configured

    @classmethod
    def get_plan_app(cls, obj):
        result = []
        for obj_plan_role in PlanRole.objects.filter(role=obj).select_related('plan').prefetch_related(
                'application_m2m'
        ):
            item_data = {
                'id': obj_plan_role.plan_id,
                'title': obj_plan_role.plan.title,
                'code': obj_plan_role.plan.code,
                'application': []
            }
            for obj_app in obj_plan_role.application_m2m.all():
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
                        'spacing_allow': obj_app.spacing_allow,
                    }
                )
            result.append(item_data)
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


class ApplicationOfRoleSerializer(serializers.ModelSerializer):
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
        model = PlanRoleApp
        fields = ('id', 'title', 'code', 'permit_mapping')
