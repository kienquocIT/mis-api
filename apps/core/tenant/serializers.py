from rest_framework import serializers

from apps.core.tenant.models import TenantPlan


class TenantPlanAppAllowPermitSerializer(serializers.ModelSerializer):
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

    @classmethod
    def get_plan(cls, obj):
        if obj.plan_id:
            return {
                'id': obj.plan_id,
                'title': obj.plan.title,
                'code': obj.plan.code,
                'application': [
                    {
                        'id': x.id,
                        'title': x.title,
                        'code': x.code,
                    } for x in obj.plan.applications.filter(allow_permit=True)
                ],
            }
        return {}

    @classmethod
    def get_license_used(cls, obj):
        if obj.license_used:
            return obj.license_used
        return 0
