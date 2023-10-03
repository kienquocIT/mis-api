from rest_framework import serializers

from apps.masterdata.saledata.models import ProductWareHouse, WareHouse, UnitOfMeasure, Account
from apps.sales.inventory.models import GoodsTransfer

__all__ = ['GoodsTransferListSerializer', 'GoodsTransferCreateSerializer', 'GoodsTransferDetailSerializer',
           'GoodsTransferUpdateSerializer']

from apps.sales.inventory.models import GoodsTransferProduct
from apps.shared import WarehouseMsg, ProductMsg, GOODS_TRANSFER_TYPE, SYSTEM_STATUS
from apps.shared.translations.goods_transfer import GTMsg


class GoodsTransferProductSerializer(serializers.ModelSerializer):
    warehouse = serializers.UUIDField()
    end_warehouse = serializers.UUIDField()
    uom = serializers.UUIDField()
    warehouse_product = serializers.UUIDField()
    tax_data = serializers.JSONField()
    unit_price = serializers.FloatField()

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
            'tax_data',
            'unit_price'
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


class GoodsTransferListSerializer(serializers.ModelSerializer):
    goods_transfer_type = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'goods_transfer_type',
            'date_transfer',
            'system_status',
        )

    @classmethod
    def get_goods_transfer_type(cls, obj):
        return str(dict(GOODS_TRANSFER_TYPE).get(obj.goods_transfer_type))

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
            'goods_transfer_type',
            'date_transfer',
            'system_status',
            'goods_transfer_datas',
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
            instance_id=data['warehouse_product']['id'],
            amount=data['quantity'],
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
                tenant=instance.tenant
            )
            bulk_data.append(obj)
            cls.update_product_amount(item, instance)
        GoodsTransferProduct.objects.bulk_create(bulk_data)
        return True

    def create(self, validated_data):
        instance = GoodsTransfer.objects.create(**validated_data)
        self.common_create_sub_goods_transfer(instance, validated_data['goods_transfer_datas'])
        return instance


class GoodsTransferDetailSerializer(serializers.ModelSerializer):
    system_status = serializers.SerializerMethodField()
    agency = serializers.SerializerMethodField()

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
    def get_system_status(cls, obj):
        return str(dict(SYSTEM_STATUS).get(obj.system_status))

    @classmethod
    def get_agency(cls, obj):
        if obj.agency:
            return {
                'id': obj.agency_id,
                'name': obj.agency.name,
            }
        return {}


class GoodsTransferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'goods_transfer_type',
            'date_transfer',
            'system_status',
        )
