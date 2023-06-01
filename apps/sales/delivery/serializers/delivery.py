from rest_framework import serializers

from ..models import OrderDelivery, OrderDeliverySub, OrderDeliveryProduct

__all__ = ['OrderDeliveryListSerializer', 'OrderDeliveryDetailSerializer']


class OrderDeliveryProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDeliveryProduct
        fields = (
            'id',
            'product_data',
            'uom_data',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
        )


class OrderDeliverySubListSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        return OrderDeliveryProductListSerializer(
            obj.orderdeliveryproduct_set.all(),
            many=True,
        ).data

    class Meta:
        model = OrderDeliverySub
        fields = (
            'id',
            'date_done',
            'previous_step',
            'times',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'products',
        )


class OrderDeliveryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'from_picking_area',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'estimated_delivery_date',
            'actual_delivery_date',
            'kind_pickup',
            'state',
            'remarks',
            'sub',
            'delivery_option',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'date_created', 'date_modified', 'is_active'
        )


class OrderDeliveryDetailSerializer(serializers.ModelSerializer):
    sub = OrderDeliverySubListSerializer()

    class Meta:
        model = OrderDelivery
        fields = (
            'id',
            'title',
            'code',
            'sale_order_id',
            'sale_order_data',
            'from_picking_area',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'estimated_delivery_date',
            'actual_delivery_date',
            'kind_pickup',
            'state',
            'remarks',
            'delivery_option',
            'delivery_quantity',
            'delivered_quantity_before',
            'remaining_quantity',
            'ready_quantity',
            'delivery_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )

    def update(self, instance, validated_data):
        # filter all sub of picking
        return instance
