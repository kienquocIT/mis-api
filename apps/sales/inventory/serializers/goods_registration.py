from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouseLot
from apps.sales.inventory.models import (
    GoodsRegistration,
    GoodsRegistrationSerial,
    GoodsRegistrationLot,
    GoodsRegistrationGeneral
)


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
        for item in obj.gre_item.all().order_by('so_item__order'):
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
                'this_available': item.this_available,
                'this_registered_value': item.this_registered_value,
                'this_available_value': item.this_available_value,
                'registered_data': [{
                    'warehouse_code': child.warehouse.code,
                    'quantity': child.quantity,
                    'cost': child.cost,
                    'value': child.value,
                    'stock_type': child.stock_type,
                    'uom_title': child.uom.title,
                    'trans_id': child.trans_id,
                    'trans_code': child.trans_code,
                    'trans_title': child.trans_title,
                    'system_date': child.system_date
                } for child in item.gre_item_sub.all().order_by('system_date', '-trans_title')]
            })
        return data_line_detail


class GoodsRegistrationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsRegistration
        fields = (
            'title',
        )


# các class cho xuất hàng dự án
class GoodsRegistrationGeneralSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsRegistrationGeneral
        fields = (
            'id',
            'quantity'
        )


class GoodsRegistrationLotSerializer(serializers.ModelSerializer):
    lot_registered = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationLot
        fields = (
            'id',
            'lot_registered'
        )

    @classmethod
    def get_lot_registered(cls, obj):
        return {
            'id': str(obj.lot_registered_id),
            'lot_number': obj.lot_registered.lot_number,
            'quantity_import': obj.lot_registered.quantity_import,
            'expire_date': obj.lot_registered.expire_date,
            'manufacture_date': obj.lot_registered.manufacture_date
        } if obj.lot_registered else None


class GoodsRegistrationSerialSerializer(serializers.ModelSerializer):
    sn_registered = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationSerial
        fields = (
            'id',
            'sn_registered',
        )

    @classmethod
    def get_sn_registered(cls, obj):
        return {
            'id': str(obj.sn_registered_id),
            'vendor_serial_number': obj.sn_registered.vendor_serial_number,
            'serial_number': obj.sn_registered.serial_number,
            'expire_date': obj.sn_registered.expire_date,
            'manufacture_date': obj.sn_registered.manufacture_date,
            'warranty_start': obj.sn_registered.warranty_start,
            'warranty_end': obj.sn_registered.warranty_end
        } if obj.sn_registered else {}


class ProjectProductListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    serial_detail = serializers.SerializerMethodField()
    lot_detail = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationGeneral
        fields = (
            'id',
            'product',
            'serial_detail',
            'lot_detail',
            'quantity'
        )

    @classmethod
    def get_product(cls, obj):
        product = obj.gre_item.product
        return {
            'id': str(product.id),
            'code': product.code,
            'title': product.title,
            'general_traceability_method': product.general_traceability_method
        } if product else {}

    @classmethod
    def get_serial_detail(cls, obj):
        serial_detail = []
        for serial in obj.gre_general_serial.filter(sn_registered__is_delete=False).order_by(
            'sn_registered__vendor_serial_number', 'sn_registered__serial_number'
        ):
            serial_detail.append({
                'id': str(serial.sn_registered_id),
                'vendor_serial_number': serial.sn_registered.vendor_serial_number,
                'serial_number': serial.sn_registered.serial_number,
                'expire_date': serial.sn_registered.expire_date,
                'manufacture_date': serial.sn_registered.manufacture_date,
                'warranty_start': serial.sn_registered.warranty_start,
                'warranty_end': serial.sn_registered.warranty_end
            })
        return serial_detail

    @classmethod
    def get_lot_detail(cls, obj):
        """ Lấy các lot của Dự án này, lấy số lượng theo bảng prd-wh """
        lot_detail = []
        for lot in obj.gre_general_lot.all():
            lot_obj = ProductWareHouseLot.objects.filter(id=lot.lot_registered_id).first()
            if lot_obj:
                lot_detail.append({
                    'id': str(lot_obj.id),
                    'lot_number': lot_obj.lot_number,
                    'quantity_import': lot_obj.quantity_import,
                    'expire_date': lot_obj.expire_date,
                    'manufacture_date': lot_obj.manufacture_date,
                    'warehouse_id': str(lot_obj.product_warehouse.warehouse_id)
                })
        return lot_detail
