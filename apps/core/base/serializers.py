from rest_framework import serializers

from apps.core.base.models import (
    SubscriptionPlan, Application, ApplicationProperty, PermissionApplication,
    Country, City, District, Ward, Currency as BaseCurrency, BaseItemUnit, IndicatorParam
)


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
                'id': x.id,
                'title': x.title,
                'code': x.code,
            } for x in obj.applications.all()
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
            'properties',
            'opp_stage_operator',
            'stage_compare_data'
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


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'title', 'code_2', 'code_3', 'language')


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'title', 'zip_code', 'country_id')


class DistrictListSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'title', 'city_id')


class WardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ('id', 'title', 'district_id')


class BaseCurrencyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseCurrency
        fields = ('id', 'title', 'code', 'title')


class BaseItemUnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseItemUnit
        fields = ('id', 'title', 'measure')


class IndicatorParamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorParam
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'syntax',
            'syntax_show',
            'example',
            'param_type'
        )


class ApplicationForPermitOpportunityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = (
            'id',
            'title',
        )
