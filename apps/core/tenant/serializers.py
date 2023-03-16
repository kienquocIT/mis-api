from rest_framework import serializers

from apps.core.tenant.models import TenantPlan, Tenant
from apps.shared import DisperseModel


class TenantPlanSerializer(serializers.ModelSerializer):
    tenant = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    license_used = serializers.SerializerMethodField()

    class Meta:
        model = TenantPlan
        fields = (
            'id',
            'tenant',
            'plan',
            'license_quantity',
            'license_used'
        )

    @classmethod
    def get_tenant(cls, obj):
        if obj.tenant_id:
            data = Tenant.objects.filter({'id': obj.tenant_id}, get_first=True)
            if data:
                return {
                    'id': data['id'],
                    'title': data['title'],
                    'code': data['code'],
                }
        return {}

    @staticmethod
    def application_of_plan(plan_id):
        plan_app_list = DisperseModel(app_model='base.PlanApplication').get_model().objects.select_related(
            'application'
        ).filter(
            plan_id=plan_id
        )
        if plan_app_list:
            return [
                {
                    'id': plan_app.application.id,
                    'title': plan_app.application.title,
                    'code': plan_app.application.code,
                } for plan_app in plan_app_list
            ]
        return []

    @classmethod
    def get_plan(cls, obj):
        if obj.plan_id:
            data = DisperseModel(app_model='base.SubscriptionPlan').get_model().objects.filter(
                {'id': obj.plan_id}, get_first=True
            )
            if data and isinstance(data, dict):
                if 'application' in data:
                    data['application'] = [
                        {
                            'id': item['id'],
                            'title': item['title'],
                            'code': item['code'],
                        } for item in data['application']
                    ]
                else:
                    data['application'] = cls.application_of_plan(obj.plan_id)
                return data
        return {}

    @classmethod
    def get_license_used(cls, obj):
        if obj.license_used:
            return obj.license_used
        return 0
