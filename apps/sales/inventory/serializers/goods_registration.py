from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouseLot, UnitOfMeasure
from apps.masterdata.saledata.serializers import ProductWareHouseListSerializer
from apps.sales.inventory.models import (
    GoodsRegistration,
    GReItemProductWarehouseSerial,
    GReItemProductWarehouseLot,
    GReItemProductWarehouse,
    GReItemBorrow,
    GReItemSub,
    GoodsRegistrationItem,
    NoneGReItemBorrow,
    NoneGReItemProductWarehouse,
    NoneGReItemProductRegisQuantity
)


def cast_unit_quantity_to_so_uom(so_uom, quantity):
    return (quantity / so_uom.ratio) if so_uom.ratio else 0


def cast_quantity_to_unit(uom, quantity):
    return quantity * uom.ratio


class GoodsRegistrationListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistration
        fields = (
            'id',
            'title',
            'code',
            'sale_order',
            'employee_created',
            'date_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}

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
                'out_delivered': item.out_delivered,
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
class GReItemSubSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    lot_mapped = serializers.SerializerMethodField()

    class Meta:
        model = GReItemSub
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
class GReItemProductWarehouseSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    stock_amount = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    available_picked = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = GReItemProductWarehouse
        fields = (
            'id',
            'product',
            'warehouse',
            'uom',
            'stock_amount',
            'picked_ready',
            'available_stock',
            'available_picked',
            'sale_order',
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
        return obj.gre_item.this_available if obj.gre_item else 0

    @classmethod
    def get_available_picked(cls, obj):
        return obj.picked_ready

    @classmethod
    def get_sale_order(cls, obj):
        if obj.gre_item:
            if obj.gre_item.so_item:
                return {
                    'id': obj.gre_item.so_item.sale_order_id,
                    'code': obj.gre_item.so_item.sale_order.code,
                    'title': obj.gre_item.so_item.sale_order.title,
                } if obj.gre_item.so_item.sale_order else {}
        return {}


class GReItemProductWarehouseLotSerializer(serializers.ModelSerializer):
    lot_registered = serializers.SerializerMethodField()

    class Meta:
        model = GReItemProductWarehouseLot
        fields = (
            'id',
            'lot_registered'
        )

    @classmethod
    def get_lot_registered(cls, obj):
        return {
            'id': str(obj.lot_registered_id),
            'lot_number': obj.lot_registered.lot_number,
            'quantity_import': obj.gre_item_prd_wh.quantity if obj.gre_item_prd_wh else 0,
            'expire_date': obj.lot_registered.expire_date,
            'manufacture_date': obj.lot_registered.manufacture_date,
            'available_stock': obj.gre_item_prd_wh.quantity if obj.gre_item_prd_wh else 0,
        } if obj.lot_registered else {}


class GReItemProductWarehouseSerialSerializer(serializers.ModelSerializer):
    sn_registered = serializers.SerializerMethodField()

    class Meta:
        model = GReItemProductWarehouseSerial
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
        model = GReItemProductWarehouse
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
        for serial in obj.gre_item_prd_wh_serial.filter(sn_registered__serial_status=0).order_by(
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
        for lot in obj.gre_item_prd_wh_lot.all():
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
class GReItemBorrowListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    borrow_uom = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    regis_data = serializers.SerializerMethodField()

    class Meta:
        model = GReItemBorrow
        fields = (
            'id',
            'quantity',
            'available',
            'available_stock',
            'product',
            'base_quantity',
            'base_available',
            'uom',
            'borrow_uom',
            'sale_order',
            'regis_data',
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': str(obj.gre_destination.sale_order_id),
            'code': obj.gre_destination.sale_order.code,
            'title': obj.gre_destination.sale_order.title,
        } if obj.gre_destination.sale_order else {}

    @classmethod
    def get_product(cls, obj):
        gre_item = obj.gre_item_source if obj.gre_item_source else obj.gre_item_destination
        if gre_item:
            return {
                'id': gre_item.product_id,
                'title': gre_item.product.title,
                'code': gre_item.product.code,
                'general_traceability_method': gre_item.product.general_traceability_method,
            } if gre_item.product else {}
        return {}

    @classmethod
    def get_uom(cls, obj):
        gre_item = obj.gre_item_source if obj.gre_item_source else obj.gre_item_destination
        if gre_item:
            if gre_item.product:
                if gre_item.product.general_uom_group:
                    return {
                        'id': gre_item.product.general_uom_group.uom_reference_id,
                        'title': gre_item.product.general_uom_group.uom_reference.title,
                        'code': gre_item.product.general_uom_group.uom_reference.code,
                        'ratio': gre_item.product.general_uom_group.uom_reference.ratio
                    } if gre_item.product.general_uom_group.uom_reference else {}
        return {}

    @classmethod
    def get_borrow_uom(cls, obj):
        return {
            'id': str(obj.uom_id),
            'title': obj.uom.title,
            'code': obj.uom.code,
            'ratio': obj.uom.ratio
        } if obj.uom else {}

    @classmethod
    def get_available_stock(cls, obj):
        return obj.base_available

    @classmethod
    def get_regis_data(cls, obj):
        result = []
        gre_item = obj.gre_item_destination
        if gre_item:
            for regis in GReItemProductWarehouseSerializer(gre_item.gre_item_prd_wh.all(), many=True).data:
                regis.update({'available_stock': obj.base_available})
                result.append(regis)
        return result


class GReItemBorrowCreateSerializer(serializers.ModelSerializer):
    gre_source = serializers.UUIDField(required=True)
    gre_item_source = serializers.UUIDField(required=True)
    uom = serializers.UUIDField(required=True)

    class Meta:
        model = GReItemBorrow
        fields = (
            'gre_source',
            'gre_item_source',
            'quantity',
            'available',
            'uom'
        )

    @classmethod
    def validate_gre_source(cls, value):
        try:
            return GoodsRegistration.objects.get(id=value)
        except GoodsRegistration.DoesNotExist:
            raise serializers.ValidationError({'goods_registration': 'Goods Registration obj does not exist.'})

    @classmethod
    def validate_gre_item_source(cls, value):
        try:
            return GoodsRegistrationItem.objects.get(id=value)
        except GoodsRegistrationItem.DoesNotExist:
            raise serializers.ValidationError({'gre_item': 'Goods Registration Item obj does not exist.'})

    @classmethod
    def validate_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get(id=value)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': 'UOM obj does not exist.'})

    def validate(self, validate_data):
        try:
            validate_data['gre_destination'] = GoodsRegistration.objects.get(
                sale_order_id=self.initial_data.get('sale_order_destination_id')
            )
            validate_data['gre_item_destination'] = GoodsRegistrationItem.objects.get(
                goods_registration=validate_data['gre_destination'],
                product=validate_data['gre_item_source'].product
            )

            # validate quantity
            if validate_data['quantity'] > 0:
                casted_quantity = cast_quantity_to_unit(validate_data['uom'], validate_data['quantity'])
                casted_quantity_limit = cast_quantity_to_unit(
                    validate_data['gre_item_destination'].so_item.unit_of_measure,
                    validate_data['gre_item_destination'].this_available
                )
                if casted_quantity > casted_quantity_limit:
                    raise serializers.ValidationError({'quantity': 'Reserved quantity > Available quantity.'})

            # validate uom
            last_borrow = GReItemBorrow.objects.filter(
                gre_item_source=validate_data['gre_item_source'],
                gre_item_destination=validate_data['gre_item_destination']
            ).first()
            if last_borrow:
                if validate_data['uom'] != last_borrow.uom:
                    raise serializers.ValidationError({'uom': 'UOM reserve must be same.'})
                validate_data['last_borrow'] = last_borrow
            return validate_data
        except Exception:
            raise serializers.ValidationError({'validate_data': 'Validation have got some errors.'})

    @classmethod
    def for_borrow(cls, validated_data):
        if 'last_borrow' in validated_data:
            last_borrow = validated_data['last_borrow']
            last_borrow.quantity += validated_data['quantity']
            last_borrow.available = last_borrow.quantity - last_borrow.delivered
            last_borrow.base_quantity = cast_quantity_to_unit(last_borrow.uom, last_borrow.quantity)
            last_borrow.base_available = cast_quantity_to_unit(last_borrow.uom, last_borrow.available)
            last_borrow.save(update_fields=['quantity', 'available', 'base_quantity', 'base_available'])
            instance = last_borrow
        else:
            instance = GReItemBorrow.objects.create(
                **validated_data,
                available=validated_data['quantity'],
                base_quantity=cast_quantity_to_unit(validated_data['uom'], validated_data['quantity']),
                base_available=cast_quantity_to_unit(validated_data['uom'], validated_data['quantity']),
            )
        return instance

    @classmethod
    def for_return_back(cls, validated_data):
        if 'last_borrow' in validated_data:
            last_borrow = validated_data['last_borrow']
            last_borrow.quantity += validated_data['quantity']
            last_borrow.available = last_borrow.quantity - last_borrow.delivered
            last_borrow.base_quantity = cast_quantity_to_unit(last_borrow.uom, last_borrow.quantity)
            last_borrow.base_available = cast_quantity_to_unit(last_borrow.uom, last_borrow.available)
            last_borrow.save(update_fields=['quantity', 'available', 'base_quantity', 'base_available'])
            return last_borrow
        raise serializers.ValidationError({'last_borrow': 'Can not find last borrow item.'})

    def create(self, validated_data):
        instance = self.for_borrow(
            validated_data
        ) if validated_data['quantity'] >= 0 else self.for_return_back(
            validated_data
        )

        # đổi sang uom đặt hàng
        borrow_quantity = cast_unit_quantity_to_so_uom(
            instance.gre_item_source.so_item.unit_of_measure,
            instance.base_quantity
        )

        # cập nhập sl mượn của dự án A
        if validated_data['quantity'] > 0:
            instance.gre_item_source.out_registered += cast_quantity_to_unit(
                validated_data['uom'],
                validated_data['quantity']
            )
        else:
            instance.gre_item_source.out_registered -= cast_quantity_to_unit(
                validated_data['uom'],
                validated_data['quantity'] * (-1)
            )
        instance.gre_item_source.out_available = (
            instance.gre_item_source.out_registered - instance.gre_item_source.out_delivered
        )
        instance.gre_item_source.save(update_fields=['out_registered', 'out_available'])

        # cập nhập sl cho mượn cho dự án B
        instance.gre_item_destination.this_registered_borrowed = borrow_quantity
        instance.gre_item_destination.this_available = instance.gre_item_destination.this_registered - borrow_quantity
        instance.gre_item_destination.save(update_fields=['this_registered_borrowed', 'this_available'])
        return instance


class GReItemBorrowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GReItemBorrow
        fields = '__all__'


class GReItemBorrowUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GReItemBorrow
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
        return cast_quantity_to_unit(obj.so_item.unit_of_measure, obj.this_available)


# các cho class cho mượn hàng từ kho chung
class NoneGReItemBorrowListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    borrow_uom = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    regis_data = serializers.SerializerMethodField()

    class Meta:
        model = NoneGReItemBorrow
        fields = (
            'id',
            'quantity',
            'available',
            'available_stock',
            'product',
            'base_quantity',
            'base_available',
            'uom',
            'borrow_uom',
            'regis_data',
        )

    @classmethod
    def get_product(cls, obj):
        gre_item = obj.gre_item_source
        if gre_item:
            return {
                'id': gre_item.product_id,
                'title': gre_item.product.title,
                'code': gre_item.product.code,
                'general_traceability_method': gre_item.product.general_traceability_method,
            } if gre_item.product else {}
        return {}

    @classmethod
    def get_uom(cls, obj):
        gre_item = obj.gre_item_source
        if gre_item:
            if gre_item.product:
                if gre_item.product.general_uom_group:
                    return {
                        'id': gre_item.product.general_uom_group.uom_reference_id,
                        'title': gre_item.product.general_uom_group.uom_reference.title,
                        'code': gre_item.product.general_uom_group.uom_reference.code,
                        'ratio': gre_item.product.general_uom_group.uom_reference.ratio
                    } if gre_item.product.general_uom_group.uom_reference else {}
        return {}

    @classmethod
    def get_borrow_uom(cls, obj):
        return {
            'id': str(obj.uom_id),
            'title': obj.uom.title,
            'code': obj.uom.code,
            'ratio': obj.uom.ratio
        } if obj.uom else {}

    @classmethod
    def get_available_stock(cls, obj):
        return obj.base_available

    @classmethod
    def get_regis_data(cls, obj):
        if obj.gre_item_source:
            if obj.gre_item_source.product:
                result = ProductWareHouseListSerializer(
                        obj.gre_item_source.product.product_warehouse_product.all(), many=True
                ).data
                for pw_data in result:
                    pw_data.update({'is_pw': True, 'common_stock': obj.base_available})
                return result
        return []


class NoneGReItemBorrowCreateSerializer(serializers.ModelSerializer):
    gre_source = serializers.UUIDField(required=True)
    gre_item_source = serializers.UUIDField(required=True)
    uom = serializers.UUIDField(required=True)

    class Meta:
        model = NoneGReItemBorrow
        fields = (
            'gre_source',
            'gre_item_source',
            'quantity',
            'available',
            'uom'
        )

    @classmethod
    def validate_gre_source(cls, value):
        try:
            return GoodsRegistration.objects.get(id=value)
        except GoodsRegistration.DoesNotExist:
            raise serializers.ValidationError({'goods_registration': 'Goods Registration obj does not exist.'})

    @classmethod
    def validate_gre_item_source(cls, value):
        try:
            return GoodsRegistrationItem.objects.get(id=value)
        except GoodsRegistrationItem.DoesNotExist:
            raise serializers.ValidationError({'gre_item': 'Goods Registration Item obj does not exist.'})

    @classmethod
    def validate_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get(id=value)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': 'UOM obj does not exist.'})

    def validate(self, validate_data):
        sum_quantity = sum(list(NoneGReItemProductWarehouse.objects.filter(
            product=validate_data['gre_item_source'].product,
        ).values_list('quantity', flat=True)))
        regis_quantity = sum(list(NoneGReItemProductRegisQuantity.objects.filter(
            product=validate_data['gre_item_source'].product,
        ).values_list('keep_for_project', flat=True)))

        # validate quantity
        if validate_data['quantity'] > 0:
            casted_quantity = cast_quantity_to_unit(validate_data['uom'], validate_data['quantity'])
            casted_quantity_limit = sum_quantity - regis_quantity
            if casted_quantity > casted_quantity_limit:
                raise serializers.ValidationError({'quantity': 'Reserved quantity > Available quantity.'})

        # validate uom
        last_borrow = NoneGReItemBorrow.objects.filter(
            gre_item_source=validate_data['gre_item_source']
        ).first()
        if last_borrow:
            if validate_data['uom'] != last_borrow.uom:
                raise serializers.ValidationError({'uom': 'UOM reserve must be same.'})
            validate_data['last_borrow'] = last_borrow
        return validate_data

    @classmethod
    def for_borrow(cls, validated_data):
        if 'last_borrow' in validated_data:
            last_borrow = validated_data['last_borrow']
            last_borrow.quantity += validated_data['quantity']
            last_borrow.available = last_borrow.quantity - last_borrow.delivered
            last_borrow.base_quantity = cast_quantity_to_unit(last_borrow.uom, last_borrow.quantity)
            last_borrow.base_available = cast_quantity_to_unit(last_borrow.uom, last_borrow.available)
            last_borrow.save(update_fields=['quantity', 'available', 'base_quantity', 'base_available'])
            instance = last_borrow
        else:
            instance = NoneGReItemBorrow.objects.create(
                **validated_data,
                available=validated_data['quantity'],
                base_quantity=cast_quantity_to_unit(validated_data['uom'], validated_data['quantity']),
                base_available=cast_quantity_to_unit(validated_data['uom'], validated_data['quantity']),
            )
        return instance

    @classmethod
    def for_return_back(cls, validated_data):
        if 'last_borrow' in validated_data:
            last_borrow = validated_data['last_borrow']
            last_borrow.quantity += validated_data['quantity']
            last_borrow.available = last_borrow.quantity - last_borrow.delivered
            last_borrow.base_quantity = cast_quantity_to_unit(last_borrow.uom, last_borrow.quantity)
            last_borrow.base_available = cast_quantity_to_unit(last_borrow.uom, last_borrow.available)
            last_borrow.save(update_fields=['quantity', 'available', 'base_quantity', 'base_available'])
            return last_borrow
        raise serializers.ValidationError({'last_borrow': 'Can not find last borrow item.'})


    def create(self, validated_data):
        instance = self.for_borrow(
            validated_data
        ) if validated_data['quantity'] >= 0 else self.for_return_back(
            validated_data
        )

        # cập nhập sl mượn của dự án A
        if validated_data['quantity'] > 0:
            instance.gre_item_source.out_registered += cast_quantity_to_unit(
                validated_data['uom'],
                validated_data['quantity']
            )
        else:
            instance.gre_item_source.out_registered -= cast_quantity_to_unit(
                validated_data['uom'],
                validated_data['quantity'] * (-1)
            )
        instance.gre_item_source.out_available = (
                instance.gre_item_source.out_registered - instance.gre_item_source.out_delivered
        )
        instance.gre_item_source.save(update_fields=['out_registered', 'out_available'])

        # update SL kho chung, (trừ đi SL mượn)
        regis_quantity_obj = NoneGReItemProductRegisQuantity.objects.filter(
            product=instance.gre_item_source.product,
        ).first()
        if regis_quantity_obj:
            if validated_data['quantity'] > 0:
                regis_quantity_obj.keep_for_project += cast_quantity_to_unit(
                    validated_data['uom'],
                    validated_data['quantity']
                )
            else:
                regis_quantity_obj.keep_for_project -= cast_quantity_to_unit(
                    validated_data['uom'],
                    validated_data['quantity'] * (-1)
                )
            regis_quantity_obj.save(update_fields=['keep_for_project'])

        return instance


class NoneGReItemBorrowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoneGReItemBorrow
        fields = '__all__'


class NoneGReItemBorrowUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoneGReItemBorrow
        fields = '__all__'

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()


class NoneGoodsRegistrationItemAvailableQuantitySerializer(serializers.ModelSerializer):
    this_available = serializers.SerializerMethodField()
    this_available_base = serializers.SerializerMethodField()
    regis_quantity = serializers.SerializerMethodField()

    class Meta:
        model = NoneGReItemProductWarehouse
        fields = (
            'id',
            'this_available',
            'this_available_base',
            'regis_quantity'
        )

    @classmethod
    def get_this_available(cls, obj):
        return obj.quantity

    @classmethod
    def get_this_available_base(cls, obj):
        return obj.quantity

    @classmethod
    def get_regis_quantity(cls, obj):
        return sum(list(NoneGReItemProductRegisQuantity.objects.filter(
            product=obj.product
        ).values_list('keep_for_project', flat=True)))


# Common serializer to get regis + borrow + from general stock
class GoodsRegisBorrowListSerializer(serializers.ModelSerializer):
    regis_data = serializers.SerializerMethodField()
    borrow_data = serializers.SerializerMethodField()
    borrow_data_general_stock = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRegistrationItem
        fields = (
            'id',
            'regis_data',
            'borrow_data',
            'borrow_data_general_stock'
        )

    @classmethod
    def get_regis_data(cls, obj):
        """
        Available = số lượng đăng ký cho chính đơn bán hàng hiện tại
        (lấy từ bảng GReItemProductWarehouse field this_available)
        """
        return GReItemProductWarehouseSerializer(obj.gre_item_prd_wh.all(), many=True).data

    @classmethod
    def get_borrow_data(cls, obj):
        """
        Available = số lượng mượn hàng từ đơn bán hàng khác
        (lấy từ bảng GReItemBorrow field base_available)
        """
        return GReItemBorrowListSerializer(obj.gre_item_src_borrow.all(), many=True).data

    @classmethod
    def get_borrow_data_general_stock(cls, obj):
        """
        Available = số lượng mượn hàng từ kho chung
        (lấy từ bảng ProductWarehouse: tổng số lượng tồn kho trừ đi hết số lượng đăng ký)
        """
        return NoneGReItemBorrowListSerializer(obj.none_gre_item_src_borrow.all(), many=True).data
