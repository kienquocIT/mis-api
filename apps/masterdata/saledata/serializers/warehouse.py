from rest_framework import serializers

from ..models import WareHouse, WareHouseStock

__all__ = [
    'WareHouseListSerializer',
    'WareHouseCreateSerializer',
    'WareHouseDetailSerializer',
    'WareHouseUpdateSerializer',
    'WarehouseStockListSerializer',
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


class WarehouseStockListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()

    @classmethod
    def get_product(cls, obj):
        if obj:
            return {
                'id': str(obj.product.id),
                'title': obj.product.title,
                'code': obj.product.code
            }
        return {}

    @classmethod
    def get_warehouse(cls, obj):
        if obj:
            return {
                'id': str(obj.warehouse.id),
                'title': obj.warehouse.title,
                'code': obj.warehouse.code
            }
        return {}

    class Meta:
        model = WareHouseStock
        fields = ('product', 'warehouse', 'stock')
