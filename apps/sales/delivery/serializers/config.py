from rest_framework import serializers

from apps.sales.delivery.models import (
    DeliveryConfig,
)

__all__ = [
    'DeliveryConfigDetailSerializer',
    'DeliveryConfigUpdateSerializer',
]


class DeliveryConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryConfig
        fields = ('id', 'is_picking', 'is_partial_ship')


class DeliveryConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryConfig
        fields = ('is_picking', 'is_partial_ship')
