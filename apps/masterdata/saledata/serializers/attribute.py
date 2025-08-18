from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.hrm.attendance.models import DeviceIntegrateEmployee, AttendanceDevice
from apps.masterdata.saledata.models import Attribute, AttributeNumeric, AttributeList, AttributeWarranty
from apps.shared import BaseMsg


class AttributeListSerializer(serializers.ModelSerializer):
    parent_n = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = (
            'id',
            'title',
            'parent_n',
            'price_config_type',
            'price_config_data',
            'is_category',
        )

    @classmethod
    def get_parent_n(cls, obj):
        return {
            'id': obj.parent_n_id,
            'title': obj.parent_n.title,
            'code': obj.parent_n.code,
        } if obj.parent_n else {}


class AttributeCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    parent_n = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Attribute
        fields = (
            'title',
            'parent_n',
            'price_config_type',
            'price_config_data',
            'is_category',
        )

    @classmethod
    def validate_parent_n(cls, value):
        try:
            if value is None:
                return value
            return Attribute.objects.get_on_company(id=value)
        except Attribute.DoesNotExist:
            raise serializers.ValidationError({'parent': BaseMsg.NOT_EXIST})

    def create(self, validated_data):
        attribute = Attribute.objects.create(**validated_data)
        if attribute.is_category is False:
            if attribute.price_config_type == 0:
                AttributeNumeric.objects.create(
                    attribute=attribute,
                    tenant_id=attribute.tenant_id,
                    company_id=attribute.company_id,
                    **attribute.price_config_data
                )

            if attribute.price_config_type == 1:
                AttributeList.objects.create(
                    attribute=attribute,
                    tenant_id=attribute.tenant_id,
                    company_id=attribute.company_id,
                    **attribute.price_config_data
                )

            if attribute.price_config_type == 2:
                AttributeWarranty.objects.create(
                    attribute=attribute,
                    tenant_id=attribute.tenant_id,
                    company_id=attribute.company_id,
                    **attribute.price_config_data
                )

        return attribute


class AttributeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceDevice
        fields = (
            'title',
            'device_ip',
            'username',
            'password',
            'minor_codes',
            'is_using',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
