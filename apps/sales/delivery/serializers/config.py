from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.sales.delivery.models import (
    DeliveryConfig,
)

__all__ = [
    'DeliveryConfigDetailSerializer',
    'DeliveryConfigUpdateSerializer',
]

from apps.shared import HRMsg


class DeliveryConfigDetailSerializer(serializers.ModelSerializer):
    lead_picking = serializers.SerializerMethodField(allow_null=True)
    lead_delivery = serializers.SerializerMethodField(allow_null=True)
    person_picking = serializers.SerializerMethodField(allow_null=True)
    person_delivery = serializers.SerializerMethodField(allow_null=True)

    @classmethod
    def get_lead_picking(cls, obj):
        if obj.lead_picking:
            return {
                "id": str(obj.id),
                "full_name": f'{obj.last_name} {obj.first_name}'
            }
        return {}

    @classmethod
    def get_lead_delivery(cls, obj):
        if obj.lead_delivery:
            return {
                "id": str(obj.id),
                "full_name": f'{obj.last_name} {obj.first_name}'
            }
        return {}

    @classmethod
    def get_person_picking(cls, obj):
        if obj.person_picking:
            person_list = []
            p_list = Employee.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=obj.person_picking
            )
            for item in p_list:
                person_list.append({
                    "id": str(item.id),
                    "full_name": f'{item.last_name} {item.first_name}'
                })
            return person_list
        return []

    class Meta:
        model = DeliveryConfig
        fields = ('id', 'is_picking', 'is_partial_ship', 'lead_picking', 'lead_delivery', 'person_picking',
                  'person_delivery')


class DeliveryConfigUpdateSerializer(serializers.ModelSerializer):
    lead_picking = serializers.SerializerMethodField(allow_null=True)
    lead_delivery = serializers.SerializerMethodField(allow_null=True)
    person_picking = serializers.SerializerMethodField(allow_null=True)
    person_delivery = serializers.SerializerMethodField(allow_null=True)

    @classmethod
    def validate_lead_picking(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_lead_delivery(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_person_picking(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_person_delivery(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    class Meta:
        model = DeliveryConfig
        fields = ('is_picking', 'is_partial_ship', 'lead_picking', 'lead_delivery', 'person_picking', 'person_delivery')
