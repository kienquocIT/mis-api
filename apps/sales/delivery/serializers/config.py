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
    lead_picking = serializers.SerializerMethodField()
    lead_delivery = serializers.SerializerMethodField()
    person_picking = serializers.SerializerMethodField()
    person_delivery = serializers.SerializerMethodField()

    @classmethod
    def get_lead_picking(cls, obj):
        if obj.lead_picking:
            return {
                "id": str(obj.lead_picking.id),
                "full_name": f'{obj.lead_picking.last_name} {obj.lead_picking.first_name}'
            }
        return {}

    @classmethod
    def get_lead_delivery(cls, obj):
        if obj.lead_delivery:
            return {
                "id": str(obj.lead_delivery.id),
                "full_name": f'{obj.lead_delivery.last_name} {obj.lead_delivery.first_name}'
            }
        return {}

    @classmethod
    def get_person_picking(cls, obj):
        if obj.person_picking:
            p_list = Employee.objects.filter_current(
                fill__company=True,
                id__in=obj.person_picking
            )
            person_list = [
                {
                    "id": str(item[0]),
                    "full_name": f'{item[2]} {item[1]}',
                    "first_name": item[1],
                    "last_name": item[2],
                } for item in p_list.values_list(
                    'id', 'first_name', 'last_name'
                )
            ]
            return person_list
        return []

    @classmethod
    def get_person_delivery(cls, obj):
        if obj.person_delivery:
            p_list = Employee.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=obj.person_delivery
            )
            person_list = [
                {
                    "id": str(item[0]),
                    "full_name": f'{item[2]} {item[1]}',
                    "first_name": item[1],
                    "last_name": item[2]
                } for item in p_list.values_list(
                    'id', 'first_name', 'last_name'
                )
            ]
            return person_list
        return []

    class Meta:
        model = DeliveryConfig
        fields = ('id', 'is_picking', 'is_partial_ship', 'lead_picking', 'lead_delivery', 'person_picking',
                  'person_delivery')


class DeliveryConfigUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryConfig
        fields = ('is_picking', 'is_partial_ship', 'lead_picking', 'lead_delivery', 'person_picking', 'person_delivery')

    @classmethod
    def validate_person_picking(cls, value):
        per_list = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=value
        )
        if len(per_list) != len(value):
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_person_delivery(cls, value):
        deli_per = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=value
        )
        if len(deli_per) != len(value):
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    # def update(self, instance, validated_data):
    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)
    #     instance.save()
    #     return instance
