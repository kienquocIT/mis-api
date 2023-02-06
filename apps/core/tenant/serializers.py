from rest_framework import serializers

from apps.core.base.models import PlanApplication
from apps.core.tenant.models import TenantPlan


class TenantPlanSerializer(serializers.ModelSerializer):
    tenant = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()

    class Meta:
        model = TenantPlan
        fields = (
            'id',
            'tenant',
            'plan'
        )

    def get_tenant(self, obj):
        if obj.tenant:
            return {
                'id': obj.tenant.id,
                'title': obj.tenant.title,
                'code': obj.tenant.code,
            }
        return {}

    def get_plan(self, obj):
        if obj.plan:
            application = []
            plan_app_list = PlanApplication.object_normal.select_related('application').filter(
                plan=obj.plan
            )
            if plan_app_list:
                for plan_app in plan_app_list:
                    application.append({
                        'id': plan_app.application.id,
                        'title': plan_app.application.title,
                        'code': plan_app.application.code,
                    })
            return {
                'id': obj.plan.id,
                'title': obj.plan.title,
                'code': obj.plan.code,
                'application': application
            }
        return {}

