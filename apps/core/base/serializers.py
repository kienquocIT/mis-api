from rest_framework import serializers

from apps.core.base.models import SubscriptionPlan, PlanApplication, Application, ApplicationProperty, PermissionApplication


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
        return [
            {
                'id': x['application__id'],
                'title': x['application__title'],
                'code': x['application__code'],
            } for x in PlanApplication.objects.filter(plan=obj).values(
                'application__id', 'application__title', 'application__code'
            )
        ]





class ApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = (
            'id',
            'title',
            'code'
        )


class ApplicationPropertyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationProperty
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'type',
            'content_type',
            'properties'
        )


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

