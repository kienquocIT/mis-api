from rest_framework import serializers
from apps.masterdata.saledata.models import WareHouse

__all__ = [
    'WareHouseListSerializer',
    'WareHouseCreateSerializer',
    'WareHouseDetailSerializer',
    'WareHouseUpdateSerializer',
]


class WareHouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = ('id', 'title', 'code', 'remarks', 'is_active')


class WareHouseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = ('title', 'code', 'remarks', 'is_active')


class WareHouseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = ('id', 'title', 'code', 'remarks', 'is_active')


class WareHouseUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, required=False)
    code = serializers.CharField(max_length=100, required=False)
    remarks = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = WareHouse
        fields = ('title', 'code', 'remarks', 'is_active')
