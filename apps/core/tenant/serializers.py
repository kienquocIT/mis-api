from rest_framework import serializers

from apps.core.tenant.models import TenantPlan, Tenant
from apps.shared import DisperseModel


class TenantPlanSerializer(serializers.ModelSerializer):
    # tenant = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    license_used = serializers.SerializerMethodField()

    class Meta:
        model = TenantPlan
        fields = (
            'id',
            # 'tenant',
            'plan',
            'license_quantity',
            'license_used'
        )

    # @classmethod
    # def get_tenant(cls, obj):
    #     if obj.tenant_id:
    #         return {
    #             'id': obj.tenant_id,
    #             'title': obj.tenant.title,
    #             'code': obj.tenant.code,
    #         }
    #     return {}

    @classmethod
    def get_plan(cls, obj):
        if obj.plan_id:
            return {
                'id': obj.plan_id,
                'title': obj.plan.title,
                'code': obj.plan.code,
                'application': [{
                    'id': x.id,
                    'title': x.title,
                    'code': x.code,
                } for x in obj.plan.applications.all()]
            }
        return {}

    @classmethod
    def get_license_used(cls, obj):
        if obj.license_used:
            return obj.license_used
        return 0
