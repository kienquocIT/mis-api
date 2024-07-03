from rest_framework import serializers

from apps.core.base.models import (
    SubscriptionPlan, Application, ApplicationProperty, PermissionApplication,
    Country, City, District, Ward, Currency as BaseCurrency, BaseItemUnit, IndicatorParam, Zones, ZonesProperties
)
from apps.shared import BaseMsg


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
    title = serializers.SerializerMethodField()

    @classmethod
    def get_title(cls, obj):
        return obj.get_title_i18n()

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
            'stage_compare_data',
            'app_code_md',
            'example',
        )


class ApplicationPropertyForPrintListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationProperty
        fields = (
            'id',
            'title',
            'code',
            'remark',
        )


class ApplicationPropertyForMailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationProperty
        fields = (
            'id',
            'title',
            'code',
            'remark',
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
        fields = ('id', 'title', 'code')


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


# ZONES
class ApplicationZonesListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    zones = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            'id',
            'title',
            'code',
            'zones',
        )

    @classmethod
    def get_title(cls, obj):
        return obj.get_title_i18n()

    @classmethod
    def get_zones(cls, obj):
        return ZonesListSerializer(obj.zones_application.all(), many=True).data


class ZonesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zones
        fields = (
            'title',
            'remark',
            'properties_data',
            'order',
        )


class ZonesCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    properties_data = serializers.ListField(child=serializers.UUIDField())

    class Meta:
        model = Zones
        fields = (
            'title',
            'remark',
            'properties_data',
            'order',
        )

    @classmethod
    def validate_properties_data(cls, value):
        if isinstance(value, list):
            property_list = ApplicationProperty.objects.filter(id__in=value)
            if property_list.count() == len(value):
                return [
                    {'id': str(prop.id), 'title': prop.title, 'code': prop.code, 'remark': prop.remark}
                    for prop in property_list
                ]
            raise serializers.ValidationError({'detail': BaseMsg.PROPERTY_NOT_EXIST})
        raise serializers.ValidationError({'detail': BaseMsg.PROPERTY_IS_ARRAY})


class ZonesCreateUpdateSerializer(serializers.ModelSerializer):
    application = serializers.UUIDField()
    zones_data = ZonesCreateSerializer(many=True)

    class Meta:
        model = Zones
        fields = (
            'application',
            'zones_data',
        )

    @classmethod
    def validate_application(cls, value):
        try:
            return Application.objects.get(id=value)
        except Application.DoesNotExist:
            raise serializers.ValidationError({'application': BaseMsg.APPLICATION_NOT_EXIST})

    def create(self, validated_data):
        zone = None
        application = validated_data.get('application', None)
        zones_data = validated_data.get('zones_data', [])
        user = self.context.get('user', None)
        if application and user:
            if all(hasattr(user, attr) for attr in ('tenant_current_id', 'company_current_id', 'employee_current_id')):
                old_zones = application.zones_application.filter(
                    tenant_id=user.tenant_current_id, company_id=user.company_current_id
                )
                if old_zones:
                    for old_zone in old_zones:
                        old_zone.zones_props_zone.all().delete()
                    old_zones.delete()
                new_zones = Zones.objects.bulk_create([
                    Zones(
                        **zone_data, application=application,
                        tenant_id=user.tenant_current_id, company_id=user.company_current_id,
                        employee_created_id=user.employee_current_id, employee_modified_id=user.employee_current_id,
                    )
                    for zone_data in zones_data
                ])
                if new_zones:
                    for new_zone in new_zones:
                        ZonesProperties.objects.bulk_create([
                            ZonesProperties(zone=new_zone, property_id=prop_data.get('id', None))
                            for prop_data in new_zone.properties_data
                        ])
                        zone = new_zone
        return zone
