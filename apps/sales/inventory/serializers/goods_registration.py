from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouseLot, UnitOfMeasure
from apps.sales.inventory.models import (
    GoodsRegistration,
    GoodsRegistrationSerial,
    GoodsRegistrationLot,
    GoodsRegistrationGeneral,
    GoodsRegistrationItemBorrow,
    GoodsRegistrationItemSub,
    GoodsRegistrationItem
)


def cast_unit_quantity_to_so_uom(so_uom, quantity):
    return (quantity / so_uom.ratio) if so_uom.ratio else 0


def cast_quantity_to_unit(uom, quantity):
    return quantity * uom.ratio


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
                'id': str(item.id),
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
                        'ratio': item.so_item.unit_of_measure.ratio
                    } if item.so_item.unit_of_measure else {},
                    'total_order': item.so_item.product_quantity,
                    'base_uom': {
                        'id': str(item.product.general_uom_group.uom_reference_id),
                        'code': item.product.general_uom_group.uom_reference.code,
                        'title': item.product.general_uom_group.uom_reference.title,
                        'ratio': item.product.general_uom_group.uom_reference.ratio
                    }
                } if item.so_item else {},
                'this_registered': item.this_registered,
                'this_available': item.this_available,
                'this_registered_borrowed': item.this_registered_borrowed,
                'out_registered': item.out_registered,
                'out_available': item.out_available
            })
        return data_line_detail


class GoodsRegistrationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsRegistration
        fields = (
            'title',
        )


# lấy dữ liệu chi tiết nhập-xuất hàng của dự án
class GoodsRegistrationItemSubSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    lot_mapped = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationItemSub
        fields = (
            'id',
            'sale_order',
            'warehouse',
            'quantity',
            'cost',
            'value',
            'stock_type',
            'uom',
            'trans_id',
            'trans_code',
            'trans_title',
            'system_date',
            'lot_mapped'
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': str(obj.gre_item.so_item.sale_order_id),
            'code': obj.gre_item.so_item.sale_order.code,
            'title': obj.gre_item.so_item.sale_order.title,
        } if obj.gre_item.so_item.sale_order else {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': str(obj.warehouse_id),
            'code': obj.warehouse.code,
            'title': obj.warehouse.title,
        } if obj.warehouse else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': str(obj.uom_id),
            'code': obj.uom.code,
            'title': obj.uom.title,
        } if obj.uom else {}

    @classmethod
    def get_lot_mapped(cls, obj):
        return {
            'id': str(obj.lot_mapped_id),
            'lot_number': obj.lot_mapped.lot_number,
        } if obj.lot_mapped else {}


# lấy hàng đăng kí theo dự án
class GoodsRegistrationGeneralSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    stock_amount = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    available_picked = serializers.SerializerMethodField()
    other_projects = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationGeneral
        fields = (
            'id',
            'product',
            'warehouse',
            'uom',
            'stock_amount',
            'picked_ready',
            'available_stock',
            'available_picked',
            'other_projects'
        )

    @classmethod
    def get_product(cls, obj):
        if obj.gre_item:
            return {
                'id': obj.gre_item.product_id,
                'title': obj.gre_item.product.title,
                'code': obj.gre_item.product.code,
                'general_traceability_method': obj.gre_item.product.general_traceability_method,
            } if obj.gre_item.product else {}
        return {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_uom(cls, obj):
        if obj.gre_item:
            if obj.gre_item.product:
                if obj.gre_item.product.general_uom_group:
                    return {
                        'id': obj.gre_item.product.general_uom_group.uom_reference_id,
                        'title': obj.gre_item.product.general_uom_group.uom_reference.title,
                        'code': obj.gre_item.product.general_uom_group.uom_reference.code,
                        'ratio': obj.gre_item.product.general_uom_group.uom_reference.ratio
                    } if obj.gre_item.product.general_uom_group.uom_reference else {}
        return {}

    @classmethod
    def get_stock_amount(cls, obj):
        return obj.quantity

    @classmethod
    def get_available_stock(cls, obj):
        return obj.quantity

    @classmethod
    def get_available_picked(cls, obj):
        return obj.picked_ready


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
            'quantity_import': obj.gre_general.quantity if obj.gre_general else 0,
            'expire_date': obj.lot_registered.expire_date,
            'manufacture_date': obj.lot_registered.manufacture_date,
            'quantity_available': obj.gre_general.quantity if obj.gre_general else 0,
        } if obj.lot_registered else {}


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


# lấy hàng dự án dành cho Goods Transfer
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


# các cho class cho mượn hàng giữa các dự án
class GoodsRegistrationItemBorrowListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationItemBorrow
        fields = (
            'id',
            'quantity',
            'available',
            'uom',
            'sale_order',
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': str(obj.goods_registration_destination.sale_order_id),
            'code': obj.goods_registration_destination.sale_order.code,
            'title': obj.goods_registration_destination.sale_order.title,
        }

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': str(obj.uom_id),
            'code': obj.uom.code,
            'title': obj.uom.title,
        }


class GoodsRegistrationItemBorrowCreateSerializer(serializers.ModelSerializer):
    goods_registration_source = serializers.UUIDField(required=True)
    gre_item_source = serializers.UUIDField(required=True)
    uom = serializers.UUIDField(required=True)

    class Meta:
        model = GoodsRegistrationItemBorrow
        fields = (
            'goods_registration_source',
            'gre_item_source',
            'quantity',
            'available',
            'uom'
        )

    @classmethod
    def validate_goods_registration_source(cls, value):
        try:
            return GoodsRegistration.objects.get(id=value)
        except GoodsRegistration.DoesNotExist:
            raise serializers.ValidationError({'goods_registration': 'Goods Registration obj is not exist.'})

    @classmethod
    def validate_gre_item_source(cls, value):
        try:
            return GoodsRegistrationItem.objects.get(id=value)
        except GoodsRegistrationItem.DoesNotExist:
            raise serializers.ValidationError({'gre_item': 'Goods Registration Item obj is not exist.'})

    @classmethod
    def validate_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get(id=value)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': 'UOM obj is not exist.'})

    def validate(self, validate_data):
        try:
            validate_data['goods_registration_destination'] = GoodsRegistration.objects.get(
                sale_order_id=self.initial_data.get('sale_order_destination_id')
            )
            validate_data['gre_item_destination'] = GoodsRegistrationItem.objects.get(
                goods_registration=validate_data['goods_registration_destination'],
                product=validate_data['gre_item_source'].product
            )
            return validate_data
        except Exception:
            raise serializers.ValidationError({'validate_data': 'Validation have got some errors.'})

    @classmethod
    def for_borrow(cls, validated_data):
        casted_quantity = cast_quantity_to_unit(validated_data['uom'], validated_data['quantity'])
        casted_quantity_limit = cast_quantity_to_unit(
            validated_data['gre_item_destination'].so_item.unit_of_measure,
            validated_data['gre_item_destination'].this_available
        )
        if casted_quantity > casted_quantity_limit:
            raise serializers.ValidationError({'quantity': 'Reserved quantity > Available quantity.'})

        last_borrow = GoodsRegistrationItemBorrow.objects.filter(
            gre_item_source=validated_data['gre_item_source'],
            gre_item_destination=validated_data['gre_item_destination']
        ).first()
        if last_borrow:
            if validated_data['uom'] != last_borrow.uom:
                raise serializers.ValidationError({'uom': 'UOM reserve must be same.'})

            last_borrow.quantity += validated_data['quantity']
            last_borrow.available += validated_data['quantity']
            last_borrow.save(update_fields=['quantity', 'available'])
            instance = last_borrow
        else:
            instance = GoodsRegistrationItemBorrow.objects.create(
                **validated_data, available=validated_data['quantity']
            )

            # đổi sang uom đặt hàng
            casted_quantity = cast_unit_quantity_to_so_uom(
                instance.gre_item_source.so_item.unit_of_measure,
                cast_quantity_to_unit(instance.uom, instance.quantity)
            )

        # cập nhập sl mượn của dự án A
        gre_item_src = validated_data['gre_item_source']
        gre_item_src.out_registered += validated_data['quantity']
        gre_item_src.out_available += validated_data['quantity']
        gre_item_src.save(update_fields=['out_registered', 'out_available'])

        # cập nhập sl cho mượn cho dự án B
        gre_item_des = validated_data['gre_item_destination']
        unit_price = gre_item_des.this_registered_value / gre_item_des.this_registered
        gre_item_des.this_registered_borrowed += validated_data['quantity']
        gre_item_des.this_registered_value_borrowed = unit_price * gre_item_des.this_registered_borrowed
        gre_item_des.this_available = gre_item_des.this_registered - gre_item_des.this_registered_borrowed
        gre_item_des.this_available_value = unit_price * gre_item_des.this_available
        gre_item_des.save(update_fields=[
            'this_registered_borrowed',
            'this_registered_value_borrowed',
            'this_available',
            'this_available_value'
        ])
        return instance

    @classmethod
    def for_return_back(cls, validated_data):
        last_borrow = GoodsRegistrationItemBorrow.objects.filter(
            gre_item_source=validated_data['gre_item_source'],
            gre_item_destination=validated_data['gre_item_destination']
        ).first()
        if last_borrow:
            if validated_data['uom'] != last_borrow.uom:
                raise serializers.ValidationError({'uom': 'UOM reserve must be same.'})

            last_borrow.quantity += validated_data['quantity']
            last_borrow.available += validated_data['quantity']
            last_borrow.save(update_fields=['quantity', 'available'])

            # cập nhập sl mượn của dự án A
            gre_item_src = validated_data['gre_item_source']
            gre_item_src.out_registered += validated_data['quantity']
            gre_item_src.out_available += validated_data['quantity']
            gre_item_src.save(update_fields=['out_registered', 'out_available'])

            # cập nhập sl cho mượn cho dự án B
            gre_item_des = validated_data['gre_item_destination']
            unit_price = gre_item_des.this_registered_value / gre_item_des.this_registered
            gre_item_des.this_registered_borrowed += validated_data['quantity']
            gre_item_des.this_registered_value_borrowed = unit_price * gre_item_des.this_registered_borrowed
            gre_item_des.this_available = gre_item_des.this_registered - gre_item_des.this_registered_borrowed
            gre_item_des.this_available_value = unit_price * gre_item_des.this_available
            gre_item_des.save(update_fields=[
                'this_registered_borrowed',
                'this_registered_value_borrowed',
                'this_available',
                'this_available_value'
            ])
        return last_borrow

    def create(self, validated_data):
        if validated_data['quantity'] > 0:
            return self.for_borrow(validated_data)
        return self.for_return_back(validated_data)


class GoodsRegistrationItemBorrowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsRegistrationItemBorrow
        fields = '__all__'


class GoodsRegistrationItemBorrowUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsRegistrationItemBorrow
        fields = '__all__'

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()


class GoodsRegistrationItemAvailableQuantitySerializer(serializers.ModelSerializer):
    this_available_base = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationItem
        fields = (
            'id',
            'this_available',
            'this_available_base'
        )

    @classmethod
    def get_this_available_base(cls, obj):
        return obj.this_available * obj.so_item.unit_of_measure.ratio
