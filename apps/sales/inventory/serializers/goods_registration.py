from rest_framework import serializers
from apps.sales.inventory.models import GoodsRegistration, GoodsRegistrationLineDetail
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


class GoodsRegistrationDetailSerializer(serializers.ModelSerializer):
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
                'so_code': item.so_item.sale_order.code,
                'so_item': {
                    'id': item.so_item_id,
                    'product': {
                        'id': item.so_item.product_id,
                        'code': item.so_item.product.code,
                        'title': item.so_item.product.title,
                        'description': item.so_item.product.description,
                        'type': item.so_item.product.general_traceability_method
                    } if item.so_item.product else {},
                    'uom': {
                        'id': item.so_item.unit_of_measure_id,
                        'code': item.so_item.unit_of_measure.code,
                        'title': item.so_item.unit_of_measure.title,
                    } if item.so_item.unit_of_measure else {},
                    'total_order': item.so_item.product_quantity
                } if item.so_item else {},
                'this_registered': item.this_registered,
                'this_others': item.this_others,
                'this_available': item.this_available,
                'this_registered_value': item.this_registered_value,
                'this_others_value': item.this_others_value,
                'this_available_value': item.this_available_value,
                'registered_data': item.registered_data,
                'out_registered': item.out_registered,
                'out_delivered': item.out_delivered,
                'out_remain': item.out_remain,
                'out_registered_value': item.out_registered_value,
                'out_delivered_value': item.out_delivered_value,
                'out_remain_value': item.out_remain_value,
            })
        return data_line_detail


class GoodsRegistrationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsRegistration
        fields = (
            'title',
        )


# các class cho xuất hàng dự án
class GoodsRegistrationProductWarehouseSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationLineDetail
        fields = (
            'sale_order',
            'product',
            'this_registered',
            'this_registered_value',
            'this_available',
            'this_available_value',
            'registered_data'
        )

    @classmethod
    def get_sale_order(cls, obj):
        sale_order = obj.so_item.sale_order
        return {
            'id': str(sale_order.id),
            'code': sale_order.code,
            'title': sale_order.title
        }

    @classmethod
    def get_product(cls, obj):
        product = obj.so_item.product
        return {
            'id': str(product.id),
            'code': product.code,
            'title': product.title
        }


class GoodsRegistrationProductWarehouseLotSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    lot_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationLineDetail
        fields = (
            'sale_order',
            'product',
            'this_registered',
            'this_registered_value',
            'this_available',
            'this_available_value',
            'registered_data',
            'lot_data'
        )

    @classmethod
    def get_sale_order(cls, obj):
        sale_order = obj.so_item.sale_order
        return {
            'id': str(sale_order.id),
            'code': sale_order.code,
            'title': sale_order.title
        }

    @classmethod
    def get_product(cls, obj):
        product = obj.so_item.product
        return {
            'id': str(product.id),
            'code': product.code,
            'title': product.title
        }

    @classmethod
    def get_lot_data(cls, obj):
        lot_data = []
        for registered in obj.goods_registration_item_lot.all():
            lot_data.append({
                'id': str(registered.lot_registered_id),
                'lot_number': registered.lot_registered.lot_number,
                'quantity_import': registered.lot_registered.quantity_import,
                'expire_date': registered.lot_registered.expire_date,
                'manufacture_date': registered.lot_registered.manufacture_date
            })
        return lot_data


class GoodsRegistrationProductWarehouseSerialSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    serial_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationLineDetail
        fields = (
            'sale_order',
            'product',
            'this_registered',
            'this_registered_value',
            'this_available',
            'this_available_value',
            'registered_data',
            'serial_data'
        )

    @classmethod
    def get_sale_order(cls, obj):
        sale_order = obj.so_item.sale_order
        return {
            'id': str(sale_order.id),
            'code': sale_order.code,
            'title': sale_order.title
        }

    @classmethod
    def get_product(cls, obj):
        product = obj.so_item.product
        return {
            'id': str(product.id),
            'code': product.code,
            'title': product.title
        }

    @classmethod
    def get_serial_data(cls, obj):
        serial_data = []
        for registered in obj.goods_registration_item_serial.all():
            serial_data.append({
                'id': str(registered.sn_registered_id),
                'vendor_serial_number': registered.sn_registered.vendor_serial_number,
                'serial_number': registered.sn_registered.serial_number,
                'expire_date': registered.sn_registered.expire_date,
                'manufacture_date': registered.sn_registered.manufacture_date,
                'warranty_start': registered.sn_registered.warranty_start,
                'warranty_end': registered.sn_registered.warranty_end
            })
        return serial_data
