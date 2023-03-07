from rest_framework import serializers

from apps.core.base.models import SubscriptionPlan, PlanApplication, PermissionApplication, Application


# Subscription Plan
class PlanListSerializer(serializers.ModelSerializer):
    application = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = (
            'id',
            'title',
            'code',
            'application'
        )

    @classmethod
    def get_application(cls, obj):
        result = []
        plan_app_list = PlanApplication.object_normal.select_related('application').filter(
            plan=obj
        )
        if plan_app_list:
            for plan_app in plan_app_list:
                result.append(
                    {
                        'id': plan_app.application.id,
                        'title': plan_app.application.title,
                        'code': plan_app.application.code,
                    }
                )
        return result


class ApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('id', 'title', 'code', 'remarks')


class PermissionApplicationListSerializer(serializers.ModelSerializer):
    extras = serializers.JSONField()
    app = serializers.SerializerMethodField()

    @classmethod
    def get_app(cls, obj):
        if obj.app:
            return {
                "id": obj.app_id,
                "title": obj.app.title,
                "code": obj.app.code,
                "remarks": obj.app.remarks,
            }
        return {}

    class Meta:
        model = PermissionApplication
        fields = ('permission', 'app', 'extras')
