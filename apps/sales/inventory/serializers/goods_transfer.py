from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import ProductWareHouse, WareHouse, UnitOfMeasure, Account
from apps.sales.inventory.models import GoodsTransfer

__all__ = ['GoodsTransferListSerializer', 'GoodsTransferCreateSerializer', 'GoodsTransferDetailSerializer',
           'GoodsTransferUpdateSerializer']

from apps.sales.inventory.models import GoodsTransferProduct
from apps.shared import WarehouseMsg, ProductMsg, GOODS_TRANSFER_TYPE, SYSTEM_STATUS, AbstractDetailSerializerModel
from apps.shared.translations.goods_transfer import GTMsg


class GoodsTransferProductSerializer(serializers.ModelSerializer):
    warehouse_product = serializers.UUIDField()
    warehouse = serializers.UUIDField()
    end_warehouse = serializers.UUIDField()
    uom = serializers.UUIDField()

    sn_changes = serializers.ListField(default=[])
    lot_changes = serializers.ListField(default=[])

    class Meta:
        model = GoodsTransferProduct
        fields = (
            'warehouse_product',
            'warehouse',
            'end_warehouse',
            'uom',
            'quantity',
            'unit_cost',
            'subtotal',
            'sn_changes',
            'lot_changes'
        )

    @classmethod
    def validate_warehouse_product(cls, value):
        try:
            product = ProductWareHouse.objects.select_related('product').get(id=value)
            return {
                'id': str(product.id),
                'product_data': {
                    'id': str(product.product_id),
                    'title': product.product.title,
                    'code': product.product.code,
                }
            }
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'warehouse_product': WarehouseMsg.PRODUCT_NOT_EXIST
                }
            )

    @classmethod
    def validate_warehouse(cls, value):
        try:
            warehouse = WareHouse.objects.get(id=value)
            return {
                'id': str(warehouse.id),
                'title': warehouse.title,
                'code': warehouse.code,
            }
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'warehouse': WarehouseMsg.WAREHOUSE_NOT_EXIST
                }
            )

    @classmethod
    def validate_end_warehouse(cls, value):
        try:
            warehouse = WareHouse.objects.get(id=value)
            return {
                'id': str(warehouse.id),
                'title': warehouse.title,
                'code': warehouse.code,
            }
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'end_warehouse': WarehouseMsg.END_WAREHOUSE_NOT_EXIST
                }
            )

    @classmethod
    def validate_uom(cls, value):
        try:
            uom = UnitOfMeasure.objects.get(id=value)
            return {
                'id': str(uom.id),
                'title': uom.title,
                'code': uom.code,
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST
                }
            )

    def validate(self, validated_data):
        return validated_data


class GoodsTransferListSerializer(serializers.ModelSerializer):
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'date_transfer',
            'system_status',
        )

    @classmethod
    def get_system_status(cls, obj):
        return str(dict(SYSTEM_STATUS).get(obj.system_status))


class GoodsTransferCreateSerializer(serializers.ModelSerializer):
    goods_transfer_datas = serializers.ListField(child=GoodsTransferProductSerializer())
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
            'goods_transfer_datas'
        )

    @classmethod
    def validate_agency(cls, value):
        try:
            return Account.objects.get(id=value)
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'agency': GTMsg.AGENCY_NOT_EXIST
                }
            )

    @classmethod
    def update_product_amount(cls, data, instance):
        ProductWareHouse.push_from_receipt(
            tenant_id=instance.tenant_id,
            company_id=instance.company_id,
            product_id=data['warehouse_product']['product_data']['id'],
            warehouse_id=data['end_warehouse']['id'],
            uom_id=data['uom']['id'],
            tax_id=data['tax_data']['id'],
            amount=data['quantity'],
            unit_price=data['unit_price']
        )
        ProductWareHouse.pop_from_transfer(
            product_warehouse_id=data['warehouse_product']['id'],
            amount=data['quantity'],
            data=data
        )
        return True

    @classmethod
    def common_create_sub_goods_transfer(cls, instance, data):
        bulk_data = []
        for item in data:
            obj = GoodsTransferProduct(
                goods_transfer=instance,
                warehouse_id=item['warehouse']['id'],
                warehouse_title=item['warehouse']['title'],
                warehouse_product_id=item['warehouse_product']['id'],
                product_id=item['warehouse_product']['product_data']['id'],
                product_title=item['warehouse_product']['product_data']['title'],
                end_warehouse_id=item['end_warehouse']['id'],
                end_warehouse_title=item['end_warehouse']['title'],
                uom_id=item['uom']['id'],
                uom_title=item['uom']['title'],
                quantity=item['quantity'],
                unit_cost=item['unit_cost'],
                subtotal=item['subtotal'],
                company=instance.company,
                tenant=instance.tenant,
                lot_data=item['lot_changes'],
                sn_data=item['sn_changes']
            )
            bulk_data.append(obj)
        GoodsTransferProduct.objects.filter(goods_transfer=instance).delete()
        GoodsTransferProduct.objects.bulk_create(bulk_data)
        return True

    @decorator_run_workflow
    def create(self, validated_data):
        instance = GoodsTransfer.objects.create(**validated_data, goods_transfer_type=0)
        self.common_create_sub_goods_transfer(instance, validated_data['goods_transfer_datas'])
        return instance


class GoodsTransferDetailSerializer(AbstractDetailSerializerModel):
    agency = serializers.SerializerMethodField()
    goods_transfer_datas = serializers.SerializerMethodField()

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
            'goods_transfer_datas'
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
    def get_goods_transfer_datas(cls, obj):
        goods_transfer_datas = []
        for item in obj.goods_transfer.all():
            serial_detail = []
            serial_exist = 0
            for serial in item.warehouse_product.product_warehouse_serial_product_warehouse.filter(
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

            lot_detail = []
            lot_is_lost = False
            for lot in item.warehouse_product.product_warehouse_lot_product_warehouse.filter(
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
            goods_transfer_datas.append({
                'product_warehouse': {
                    'id': item.warehouse_product_id,
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
        return goods_transfer_datas


class GoodsTransferUpdateSerializer(serializers.ModelSerializer):
    goods_transfer_datas = serializers.ListField(child=GoodsTransferProductSerializer())
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
            'goods_transfer_datas'
        )

    def validate(self, validated_data):
        return validated_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        GoodsTransferCreateSerializer.common_create_sub_goods_transfer(instance, validated_data['goods_transfer_datas'])
        return instance
