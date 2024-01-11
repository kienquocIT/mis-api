from rest_framework import serializers
from apps.core.base.models import BaseItemUnit
from apps.masterdata.saledata.models.revenue_plan_config import (
    RevenuePlanConfig, RevenuePlanConfigRoles
)
from apps.shared import ProductMsg


# Product Type
class RevenuePlanConfigListSerializer(serializers.ModelSerializer):  # noqa
    roles_mapped_list = serializers.SerializerMethodField()

    class Meta:
        model = RevenuePlanConfig
        fields = ('id', 'roles_mapped_list')

    @classmethod
    def get_roles_mapped_list(cls, obj):
        return [{
            'id': item.roles_mapped_id,
            'title': item.roles_mapped.title
        } for item in obj.revenue_plan_config_mapped.all()]


class RevenuePlanConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenuePlanConfig
        fields = ('roles_mapped_list',)

    def create(self, validated_data):
        config = RevenuePlanConfig.objects.create(**validated_data)
        bulk_info = []
        for roles_mapped in validated_data.get('roles_mapped_list', []):
            bulk_info.append(RevenuePlanConfigRoles(revenue_plan_config=config, roles_mapped_id=roles_mapped))
        RevenuePlanConfig.objects.filter(company=config.company).exclude(id=config.id).delete()
        RevenuePlanConfigRoles.objects.bulk_create(bulk_info)
        return config


class RevenuePlanConfigDetailSerializer(serializers.ModelSerializer):
    roles_mapped_list = serializers.SerializerMethodField()

    class Meta:
        model = RevenuePlanConfig
        fields = ('id', 'roles_mapped_list')

    @classmethod
    def get_roles_mapped_list(cls, obj):
        return [{
            'id': item.roles_mapped_id,
            'title': item.roles_mapped.title
        } for item in obj.revenue_plan_config_mapped.all()]
