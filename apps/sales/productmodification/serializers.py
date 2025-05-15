from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, Product

__all__ = [
    'WarehouseListByProductSerializer',
]


class ProductModifiedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_traceability_method'
        )


class ProductComponentListSerializer(serializers.ModelSerializer):
    component_list_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'component_list_data'
        )

    @classmethod
    def get_component_list_data(cls, obj):
        component_list_data = []
        for item in obj.product_components.all():
            component_list_data.append({
                'order': item.order,
                'id': item.id,
                'component_name': item.component_name,
                'component_des': item.component_des,
                'component_quantity': item.component_quantity
            })
        return component_list_data


class WarehouseListByProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'warehouse_data',
            'uom_data',
            'stock_amount'
        )


class ProductSerialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseSerial
        fields = (
            'id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end'
        )
