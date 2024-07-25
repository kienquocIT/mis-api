from django.db import transaction
from rest_framework import serializers

from apps.sales.delivery.models import (OrderPickingProduct, OrderPickingSub)
from apps.shared.translations.sales import DeliverMsg
from ..utils import DeliHandler, PickingHandler

__all__ = [
    'OrderPickingListSerializer',
    'OrderPickingSubDetailSerializer',
    'OrderPickingProductListSerializer',
    'OrderPickingSubListSerializer',
    'OrderPickingSubUpdateSerializer',
]


class OrderPickingProductListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()
    uom_data = serializers.SerializerMethodField()

    class Meta:
        model = OrderPickingProduct
        fields = (
            'id',
            'order',
            'is_promotion',
            'product_data',
            'uom_data',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
        )

    @classmethod
    def get_uom_data(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
            'ratio': obj.uom.ratio
        } if obj.uom else {}

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'remarks': obj.product.description,
            'uom_inventory': {
                'id': obj.product.inventory_uom_id,
                'title': obj.product.inventory_uom.title,
                'code': obj.product.inventory_uom.code,
                'ratio': obj.product.inventory_uom.ratio,
            } if obj.product.inventory_uom else {}
        } if obj.product else {}


class OrderPickingSubListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": obj.employee_inherit_id,
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    class Meta:
        model = OrderPickingSub
        fields = (
            'id',
            'code',
            'sale_order_data',
            'date_created',
            'state',
            'estimated_delivery_date',
            'employee_inherit'
        )


class OrderPickingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPickingSub
        fields = (
            'code',
            'sale_order_data',
            'date_created',
            'estimated_delivery_date',
            'employee_inherit',
            'state',
        )


class OrderPickingSubDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_products(cls, obj):
        return OrderPickingProductListSerializer(
            obj.picking_product_picking_sub.all(),
            many=True,
        ).data

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                "id": str(obj.employee_inherit_id),
                "full_name": f'{obj.employee_inherit.last_name} {obj.employee_inherit.first_name}'
            }
        return {}

    class Meta:
        model = OrderPickingSub
        fields = (
            'id',
            'code',
            'order_picking',
            'sale_order_data',
            'ware_house_data',
            'estimated_delivery_date',
            'state',
            'remarks',
            'to_location',
            'products',
            'pickup_quantity',
            'picked_quantity_before',
            'remaining_quantity',
            'picked_quantity',
            'delivery_option',
            'employee_inherit'
        )


class ProductPickingUpdateSerializer(serializers.Serializer):  # noqa
    product_id = serializers.UUIDField()
    done = serializers.IntegerField(min_value=1)
    delivery_data = serializers.JSONField()
    order = serializers.IntegerField(min_value=1)


class OrderPickingSubUpdateSerializer(serializers.ModelSerializer):
    products = ProductPickingUpdateSerializer(many=True)
    sale_order_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    delivery_option = serializers.IntegerField(min_value=0)

    @classmethod
    def validate_state(cls, value):
        if value == 1:
            raise serializers.ValidationError(
                {
                    'state': DeliverMsg.ERROR_STATE
                }
            )
        return value

    def validate(self, validate_data):
        if len(validate_data['products']) > 0 and 'estimated_delivery_date' not in validate_data:
            raise serializers.ValidationError(
                {
                    'detail': DeliverMsg.ERROR_ESTIMATED_DATE
                }
            )
        return validate_data

    def update(self, instance, validated_data):
        # convert prod to dict
        product_done = {}
        picked_quantity_total = 0
        DeliHandler.check_update_prod_and_emp(instance, validated_data)
        print('check update pass')

        if 'products' in validated_data and len(validated_data['products']) > 0:
            for item in validated_data['products']:
                item_key = str(item['product_id']) + "___" + str(item['order'])
                picked_quantity_total += item['done']
                product_done[item_key] = {
                    'stock': item['done'],
                    'delivery_data': item['delivery_data']
                }
            instance.estimated_delivery_date = validated_data['estimated_delivery_date']
            instance.remarks = validated_data['remarks']
            instance.to_location = validated_data['to_location']
            instance.ware_house = validated_data['ware_house']
            try:
                with transaction.atomic():
                    # update picking prod và delivery prod trừ vào warehouse stock
                    pickup_data = PickingHandler.update_prod_current(instance, product_done, picked_quantity_total)
                    PickingHandler.update_current_sub(instance, pickup_data, picked_quantity_total)
            except Exception as err:
                print(err)
                raise err
        else:
            del validated_data['products']
            del validated_data['state']
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            instance.order_picking.employee_inherit = instance.employee_inherit
            instance.order_picking.save()
        return instance

    class Meta:
        model = OrderPickingSub
        fields = ('products', 'sale_order_id', 'order_picking', 'state', 'estimated_delivery_date', 'ware_house',
                  'to_location', 'remarks', 'delivery_option', 'employee_inherit_id')
