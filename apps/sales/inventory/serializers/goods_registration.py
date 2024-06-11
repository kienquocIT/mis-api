from rest_framework import serializers
from apps.sales.inventory.models import GoodsRegistration
from apps.shared import AbstractDetailSerializerModel


class GoodsRegistrationListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistration
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'date_created'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
            'sale_person': {
                'id': obj.sale_order.employee_inherit_id,
                'code': obj.sale_order.employee_inherit.code,
                'fullname': obj.sale_order.employee_inherit.get_full_name(2)
            } if obj.sale_order.employee_inherit else {}
        } if obj.sale_order else {}


class GoodsRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsRegistration
        fields = ()


class GoodsRegistrationDetailSerializer(AbstractDetailSerializerModel):
    sale_order = serializers.SerializerMethodField()
    data_line_detail = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistration
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'data_line_detail',
            'date_created'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'code': obj.sale_order.code,
            'title': obj.sale_order.title,
            'sale_person': {
                'id': obj.sale_order.employee_inherit_id,
                'code': obj.sale_order.employee_inherit.code,
                'fullname': obj.sale_order.employee_inherit.get_full_name(2)
            }
        }

    @classmethod
    def get_data_line_detail(cls, obj):
        data_line_detail = []
        for item in obj.goods_registration_line_detail.all().order_by('so_item__order'):
            data_line_detail.append({
                'so_item': {
                    'id': item.so_item_id,
                    'product': {
                        'id': item.so_item.product_id,
                        'code': item.so_item.product.code,
                        'title': item.so_item.product.title,
                    } if item.so_item.product else {},
                    'uom': {
                        'id': item.so_item.unit_of_measure_id,
                        'code': item.so_item.unit_of_measure.code,
                        'title': item.so_item.unit_of_measure.title,
                    } if item.so_item.unit_of_measure else {},
                    'total_order': item.so_item.product_quantity
                } if item.so_item else {},
                'registered_quantity': item.registered_quantity,
                'registered_data': item.registered_data,
            })
        return data_line_detail


class GoodsRegistrationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsRegistration
        fields = (
            'title',
        )
