from rest_framework import serializers

from apps.masterdata.saledata.models import  ProductWareHouse, WareHouse, UnitOfMeasure
from apps.sales.inventory.models import GoodsTransfer

__all__ = ['GoodsTransferListSerializer', 'GoodsTransferCreateSerializer', 'GoodsTransferDetailSerializer',
           'GoodsTransferUpdateSerializer']

from apps.sales.inventory.models import GoodsTransferProduct
from apps.shared import WarehouseMsg, ProductMsg


class GoodsTransferProductSerializer(serializers.ModelSerializer):
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
        )

    @classmethod
    def validate_product(cls, value):
        try:
            product = ProductWareHouse.objects.get(id=value).select_related('product')
            return {
                'product_warehouse_id': product.id,
                'product_id': product.product_id,
                'title': product.product.title,
            }
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError({
                'warehouse_product': WarehouseMsg.PRODUCT_NOT_EXIST
            })

    @classmethod
    def validate_warehouse(cls, value):
        try:
            warehouse = WareHouse.objects.get(id=value)
            return {
                'id': warehouse.id,
                'title': warehouse.product.title,
            }
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({
                'warehouse': WarehouseMsg.WAREHOUSE_NOT_EXIST
            })

    @classmethod
    def validate_end_warehouse(cls, value):
        try:
            warehouse = WareHouse.objects.get(id=value)
            return {
                'id': warehouse.id,
                'title': warehouse.product.title,
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
                'id': uom.id,
                'title': uom.product.title,
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST
                }
            )


class GoodsTransferListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'type',
            'date_transfer',
            'system_status',
        )


class GoodsTransferCreateSerializer(serializers.ModelSerializer):
    products_data = serializers.ListField(child=GoodsTransferProductSerializer())

    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'type',
            'date_transfer',
            'system_status',
            'products_data',
        )


class GoodsTransferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'type',
            'date_transfer',
            'system_status',
        )


class GoodsTransferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsTransfer
        fields = (
            'id',
            'code',
            'title',
            'type',
            'date_transfer',
            'system_status',
        )
