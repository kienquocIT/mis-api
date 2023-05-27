from rest_framework import serializers

from apps.sales.delivery.models import OrderPicking, OrderPickingProduct, OrderPickingSub, OrderDelivery

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
        xx = OrderPickingProductListSerializer(
            obj.orderpickingproduct_set.all(),
            many=True,
        ).data
        return xx

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
            'to_location',
            'delivery_option',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'pickup_data',
            'sub',
            'date_created', 'date_modified', 'is_active'
        )

    @classmethod
    def validate(cls, validate_data):
        if not validate_data['sub']['products']:
            raise serializers.ValidationError({"sub": 'Done field is not empty'})
        return validate_data

    @staticmethod
    def create_delivery_sub(picking_sub, picked_total, sale_order_id, delivery_opt):
        remain = picking_sub.get('remaining_quantity', 0)
        if remain == picked_total:
            delivery = OrderDelivery.objects.filter(sale_order_id=sale_order_id)
            # giao hàng 1 lần delivery = 1 giao nhiều lần delivery = 0
            # state = 0 (wait). state = 1 giao nhiều lần (Partial). state = 2 giao 1 lần (full)
            delivery.state = 2 if delivery_opt == 0 else 1
            # delivery.save()

    @staticmethod
    def update_order_picking_product(validated_data, sub_product_list):
        pickup_data_temp = {}
        picked_quantity_total = 0
        for sub_product in sub_product_list:
            for product in validated_data['sub']['products']:
                if sub_product.id == product['id']:
                    sub_product.picked_quantity = product['picked_quantity']
                    # sub_product.save()
                    pickup_data_temp[product['id']] = {
                        'remaining_quantity': sub_product.get('remaining_quantity', 0),
                        'picked_quantity': product['picked_quantity'],
                        'pickup_quantity': sub_product.get('pickup_quantity', 0),
                        'picked_quantity_before': sub_product.get('picked_quantity_before', 0)
                    }
                    picked_quantity_total += product['picked_quantity']

        return pickup_data_temp, picked_quantity_total

    def update(self, instance, validated_data):
        # filter all sub of picking
        sub_product_ids = [product['id'] for product in validated_data['sub']['products']]
        sub_product_list = OrderPickingProduct.objects.filter(validated_data['sub']['id'], id__in=sub_product_ids)
        picking_sub = OrderPickingSub.objects.filter(id=validated_data['sub'].id)
        # update picked_quantity to OrderPickingProduct
        pickup_data, picked_total = self.update_order_picking_product(validated_data, sub_product_list)
        # update OrderPickingSub
        picking_sub.pickup_data = pickup_data
        picking_sub.picked_quantity = picked_total
        # picking_sub.save()
        # active after picking all done
        self.create_delivery_sub(
            pickup_data,
            picked_total,
            validated_data.get('sale_order_id', None),
            validated_data.get('delivery_option', 0)
        )
        return instance
