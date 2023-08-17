from rest_framework import serializers

from apps.core.base.models import SubscriptionPlan, Application
from apps.core.hr.models import PlanEmployee, PlanRole
from apps.core.tenant.models import TenantPlan
from apps.shared import BaseMsg, HRMsg, Caching

__all__ = [
    'HasPermPlanAppCreateSerializer',
    'HasPermPlanAppUpdateSerializer',
    'set_up_data_plan_app',
    'validate_license_used',
    'create_plan_employee_update_tenant_plan',
    'create_plan_role_update_tenant_plan',
]


class HasPermPlanAppCreateSerializer(serializers.Serializer):  # noqa
    plan = serializers.UUIDField()
    application = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    license_used = serializers.IntegerField(required=False)
    license_quantity = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    @classmethod
    def validate_plan(cls, value):
        try:
            return SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError({'plan': BaseMsg.PLAN_NOT_EXIST})

    @classmethod
    def validate_application(cls, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            raise serializers.ValidationError({"application": BaseMsg.APPLICATIONS_NOT_EXIST})
        raise serializers.ValidationError({"application": BaseMsg.APPLICATION_IS_ARRAY})


class HasPermPlanAppUpdateSerializer(serializers.Serializer):  # noqa
    plan = serializers.UUIDField(required=False)
    application = serializers.ListSerializer(
        child=serializers.UUIDField(required=False),
        required=False
    )
    license_used = serializers.IntegerField(required=False)
    license_quantity = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    @classmethod
    def validate_plan(cls, value):
        try:
            return SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError({'plan': BaseMsg.PLAN_NOT_EXIST})

    @classmethod
    def validate_application(cls, value):
        if isinstance(value, list):
            app_list = Application.objects.filter(id__in=value)
            if app_list.count() == len(value):
                return app_list
            raise serializers.ValidationError({"application": BaseMsg.APPLICATIONS_NOT_EXIST})
        raise serializers.ValidationError({"application": BaseMsg.APPLICATION_IS_ARRAY})


def set_up_data_plan_app(validated_data, instance=None, employee_or_role='employee'):
    if employee_or_role == 'employee':
        cls_query = PlanEmployee
        filter_query = {'employee': instance}
    else:
        cls_query = PlanRole
        filter_query = {'role': instance}

    plan_application_dict = {}
    plan_app_data = []
    bulk_info = []
    if 'plan_app' in validated_data:
        plan_app_data = validated_data['plan_app']
        del validated_data['plan_app']
        if instance:
            # delete old M2M PlanEmployee
            plan_x_old = cls_query.objects.filter(**filter_query)
            if plan_x_old:
                plan_x_old.delete()
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
                    cls_query(
                        **{
                            'plan': plan_app['plan'],
                            'application': [str(app.id) for app in plan_app['application']]
                        }
                    )
                )
    return plan_application_dict, plan_app_data, bulk_info


def validate_license_used(validate_data):
    plan_license_check = ""
    if 'user' in validate_data and 'plan_app' in validate_data:
        for plan_app in validate_data['plan_app']:
            if 'plan' in plan_app and 'license_used' in plan_app and 'license_quantity' in plan_app:
                if plan_app['license_quantity']:
                    if plan_app['license_used'] > plan_app['license_quantity']:
                        plan_license_check += plan_app['plan'].title + ", "
    if plan_license_check:
        raise serializers.ValidationError(
            {
                'detail': HRMsg.EMPLOYEE_PLAN_APP_CHECK.format(plan_license_check)
            }
        )
    return validate_data


def create_plan_employee_update_tenant_plan(employee, plan_app_data, bulk_info):
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
    Caching().clean_by_prefix_many(table_name_list=['hr_PlanEmployee', 'tenant_TenantPlan'])
    return True


def create_plan_role_update_tenant_plan(role, plan_app_data, bulk_info):
    if role and plan_app_data and bulk_info:
        # create M2M PlanEmployee
        for info in bulk_info:
            info.role = role
        PlanRole.objects.bulk_create(bulk_info)
        # update TenantPlan
        for plan_data in plan_app_data:
            if 'plan' in plan_data and 'license_used' in plan_data:
                tenant_plan = TenantPlan.objects.filter(
                    tenant=role.tenant,
                    plan=plan_data['plan']
                ).first()
                if tenant_plan:
                    tenant_plan.license_used = plan_data['license_used']
                    tenant_plan.save()
    Caching().clean_by_prefix_many(table_name_list=['hr_PlanRole', 'tenant_TenantPlan'])
    return True
