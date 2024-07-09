from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import ProductWareHouse, WareHouse, UnitOfMeasure, Account, ProductWareHouseLot, \
    ProductWareHouseSerial, Product
from apps.sales.inventory.models import GoodsTransfer, GoodsTransferProduct
from apps.sales.saleorder.models import SaleOrder
from apps.shared import WarehouseMsg, ProductMsg, SaleMsg, SYSTEM_STATUS, AbstractDetailSerializerModel
from apps.shared.translations.goods_transfer import GTMsg

__all__ = [
    'GoodsTransferListSerializer',
    'GoodsTransferCreateSerializer',
    'GoodsTransferDetailSerializer',
    'GoodsTransferUpdateSerializer'
]


class GoodsTransferProductSerializer(serializers.ModelSerializer):
    product_warehouse = serializers.UUIDField()
    product = serializers.UUIDField()
    warehouse = serializers.UUIDField()
    end_warehouse = serializers.UUIDField()
    uom = serializers.UUIDField()
    sale_order_id = serializers.UUIDField(required=False)
    sn_data = serializers.ListField(default=[])
    lot_data = serializers.ListField(default=[])

    class Meta:
        model = GoodsTransferProduct
        fields = (
            'product_warehouse',
            'warehouse',
            'product',
            'sale_order',
            'end_warehouse',
            'uom',
            'lot_data',
            'sn_data',
            'quantity',
            'unit_cost',
            'subtotal'
        )

    @classmethod
    def validate_product_warehouse(cls, value):
        try:
            return ProductWareHouse.objects.select_related('product').get(id=value)
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError({'product_warehouse': WarehouseMsg.PRODUCT_WAREHOUSE_NOT_EXIST})

    @classmethod
    def validate_warehouse(cls, value):
        try:
            return WareHouse.objects.get(id=value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': WarehouseMsg.WAREHOUSE_NOT_EXIST})

    @classmethod
    def validate_product(cls, value):
        try:
            return Product.objects.get(id=value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.DOES_NOT_EXIST})

    @classmethod
    def validate_sale_order(cls, value):
        try:
            return SaleOrder.objects.get(id=value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'sale order': SaleMsg.SALE_ORDER_NOT_EXIST})

    @classmethod
    def validate_end_warehouse(cls, value):
        try:
            return WareHouse.objects.get(id=value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'end warehouse': WarehouseMsg.END_WAREHOUSE_NOT_EXIST})

    @classmethod
    def validate_uom(cls, value):
        try:
            return UnitOfMeasure.objects.get(id=value)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})

    def validate(self, validated_data):
        return validated_data


class GoodsTransferListSerializer(serializers.ModelSerializer):
    system_status = serializers.SerializerMethodField()
    raw_system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'date_transfer',
            'system_status',
            'raw_system_status'
        )

    @classmethod
    def get_system_status(cls, obj):
        return _(str(dict(SYSTEM_STATUS).get(obj.system_status)))

    @classmethod
    def get_raw_system_status(cls, obj):
        return obj.system_status


class GoodsTransferCreateSerializer(serializers.ModelSerializer):
    goods_transfer_data = serializers.ListField(child=GoodsTransferProductSerializer())
    agency = serializers.UUIDField(required=False)
    date_transfer = serializers.DateTimeField()

    class Meta:
        model = GoodsTransfer
        fields = (
            'title',
            'note',
            'agency',
            'date_transfer',
            'system_status',
            'goods_transfer_data'
        )

    @classmethod
    def validate_agency(cls, value):
        try:
            return Account.objects.get(id=value)
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError({'agency': GTMsg.AGENCY_NOT_EXIST})

    @classmethod
    def common_create_sub_goods_transfer(cls, instance, data):
        bulk_data = []
        for item in data:
            obj = GoodsTransferProduct(goods_transfer=instance, **item)
            bulk_data.append(obj)
        GoodsTransferProduct.objects.filter(goods_transfer=instance).delete()
        GoodsTransferProduct.objects.bulk_create(bulk_data)
        return True

    @decorator_run_workflow
    def create(self, validated_data):
        goods_transfer_data = validated_data['goods_transfer_data']
        del validated_data['goods_transfer_data']
        instance = GoodsTransfer.objects.create(**validated_data, goods_transfer_type=0)
        self.common_create_sub_goods_transfer(instance, goods_transfer_data)
        return instance


class GoodsTransferDetailSerializer(AbstractDetailSerializerModel):
    agency = serializers.SerializerMethodField()
    goods_transfer_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'goods_transfer_type',
            'date_transfer',
            'system_status',
            'agency',
            'note',
            'goods_transfer_data'
        )

    @classmethod
    def get_agency(cls, obj):
        if obj.agency:
            return {
                'id': obj.agency_id,
                'name': obj.agency.name,
            }
        return {}

    @classmethod
    def get_goods_transfer_data_finished(cls, item, lot_detail, serial_detail):
        serial_exist = len(item.sn_data)
        all_sn = ProductWareHouseSerial.objects.filter(id__in=item.sn_data)
        for each in all_sn:
            serial_detail.append({
                'id': each.id,
                'vendor_serial_number': each.vendor_serial_number,
                'serial_number': each.serial_number,
                'expire_date': each.expire_date,
                'manufacture_date': each.manufacture_date,
                'warranty_start': each.warranty_start,
                'warranty_end': each.warranty_end
            })
        lot_is_lost = False
        all_lot = ProductWareHouseLot.objects.filter(id__in=[lot['lot_id'] for lot in item.lot_data])
        for each in all_lot:
            lot_detail.append({
                'id': each.id,
                'lot_number': each.lot_number,
                'quantity_import': each.quantity_import,
                'expire_date': each.expire_date,
                'manufacture_date': each.manufacture_date
            })
        return lot_is_lost, serial_exist

    @classmethod
    def get_goods_transfer_data_not_finished(cls, item, lot_detail, serial_detail):
        serial_exist = 0
        for serial in item.product_warehouse.product_warehouse_serial_product_warehouse.filter(
                is_delete=False
        ).order_by('vendor_serial_number', 'serial_number'):
            serial_exist += 1 if str(serial.id) in item.sn_data else 0
            serial_detail.append({
                'id': serial.id,
                'vendor_serial_number': serial.vendor_serial_number,
                'serial_number': serial.serial_number,
                'expire_date': serial.expire_date,
                'manufacture_date': serial.manufacture_date,
                'warranty_start': serial.warranty_start,
                'warranty_end': serial.warranty_end
            })
        lot_is_lost = False
        for lot in item.product_warehouse.product_warehouse_lot_product_warehouse.filter(
                quantity_import__gt=0
        ).order_by('lot_number'):
            for each in item.lot_data:
                if each['lot_id'] == str(lot.id):
                    if each['quantity'] > lot.quantity_import:
                        lot_is_lost = True
            lot_detail.append({
                'id': lot.id,
                'lot_number': lot.lot_number,
                'quantity_import': lot.quantity_import,
                'expire_date': lot.expire_date,
                'manufacture_date': lot.manufacture_date
            })
        return lot_is_lost, serial_exist

    @classmethod
    def get_goods_transfer_data(cls, obj):
        goods_transfer_data = []
        for item in obj.goods_transfer.all():
            serial_detail = []
            lot_detail = []

            if obj.system_status not in [2, 3]:
                lot_is_lost, serial_exist = cls.get_goods_transfer_data_not_finished(item, lot_detail, serial_detail)
            else:
                lot_is_lost, serial_exist = cls.get_goods_transfer_data_finished(item, lot_detail, serial_detail)

            goods_transfer_data.append({
                'product_warehouse': {
                    'id': item.product_warehouse_id,
                    'product': {
                        'id': item.product_id,
                        'code': item.product.code,
                        'title': item.product.title,
                        'description': item.product.description,
                        'general_traceability_method': item.product.general_traceability_method,
                        'serial_detail': serial_detail,
                        'lot_detail': lot_detail
                    } if item.product else {},
                    'uom': {
                        'id': item.uom_id,
                        'code': item.uom.code,
                        'title': item.uom.title
                    } if item.uom else {},
                    'from_warehouse_mapped': {
                        'id': item.warehouse_id,
                        'code': item.warehouse.code,
                        'title': item.warehouse.title
                    } if item.warehouse else {},
                    'end_warehouse_mapped': {
                        'id': item.end_warehouse_id,
                        'code': item.end_warehouse.code,
                        'title': item.end_warehouse.title
                    } if item.end_warehouse else {}
                },
                'quantity': item.quantity,
                'unit_cost': item.unit_cost,
                'subtotal': item.subtotal,
                'lot_is_lost': lot_is_lost,
                'lot_data': item.lot_data,
                'serial_is_lost': serial_exist < len(item.sn_data),
                'sn_data': item.sn_data
            })
        return goods_transfer_data


class GoodsTransferUpdateSerializer(serializers.ModelSerializer):
    goods_transfer_data = serializers.ListField(child=GoodsTransferProductSerializer())
    agency = serializers.UUIDField(required=False)
    date_transfer = serializers.DateTimeField()

    class Meta:
        model = GoodsTransfer
        fields = (
            'title',
            'note',
            'agency',
            'date_transfer',
            'system_status',
            'goods_transfer_data'
        )

    def validate(self, validated_data):
        return validated_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        goods_transfer_data = validated_data['goods_transfer_data']
        del validated_data['goods_transfer_data']
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        GoodsTransferCreateSerializer.common_create_sub_goods_transfer(instance, goods_transfer_data)
        return instance
