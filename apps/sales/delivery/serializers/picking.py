from rest_framework import serializers

from apps.sales.delivery.models import OrderPicking, OrderPickingProduct, OrderPickingSub

__all__ = [
    'OrderPickingListSerializer',
    'OrderPickingDetailSerializer',
    'OrderPickingProductListSerializer',
]


class OrderPickingProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPickingProduct
        fields = (
            'id',
            'product_data',
            'uom_data',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
        )


class OrderPickingSubListSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        return OrderPickingProductListSerializer(
            obj.orderpickingproduct_set.all(),
            many=True,
        ).data

    class Meta:
        model = OrderPickingSub
        fields = (
            'id',
            'date_done',
            'previous_step',
            'times',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'products',
        )


class OrderPickingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPicking
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'ware_house_id',
            'ware_house_data',
            'estimated_delivery_date',
            'state',
            'remarks',
            'delivery_option',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )


class OrderPickingDetailSerializer(serializers.ModelSerializer):
    sub = OrderPickingSubListSerializer()

    class Meta:
        model = OrderPicking
        fields = (
            'id',
            'code',
            'sale_order_id',
            'sale_order_data',
            'ware_house_id',
            'ware_house_data',
            'estimated_delivery_date',
            'state',
            'remarks',
            'delivery_option',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )
