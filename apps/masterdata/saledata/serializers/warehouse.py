from rest_framework import serializers

from apps.masterdata.saledata.models import (
    WareHouse, WareHouseStock,
    ProductWareHouse,
)

__all__ = [
    'WareHouseListSerializer',
    'WareHouseCreateSerializer',
    'WareHouseDetailSerializer',
    'WareHouseUpdateSerializer',
    'WarehouseStockListSerializer',
    'ProductWareHouseStockListSerializer',
]

from apps.shared import TypeCheck


class WareHouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = ('id', 'title', 'code', 'remarks', 'is_active')


class WareHouseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = ('title', 'code', 'remarks', 'is_active')


class WareHouseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = ('id', 'title', 'code', 'remarks', 'is_active')


class WareHouseUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, required=False)
    code = serializers.CharField(max_length=100, required=False)
    remarks = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = WareHouse
        fields = ('title', 'code', 'remarks', 'is_active')


class WarehouseStockListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()

    @classmethod
    def get_product(cls, obj):
        if obj:
            return {
                'id': str(obj.product.id),
                'title': obj.product.title,
                'code': obj.product.code
            }
        return {}

    @classmethod
    def get_warehouse(cls, obj):
        if obj:
            return {
                'id': str(obj.warehouse.id),
                'title': obj.warehouse.title,
                'code': obj.warehouse.code
            }
        return {}

    class Meta:
        model = WareHouseStock
        fields = ('product', 'warehouse', 'stock')


class ProductWareHouseStockListSerializer(serializers.ModelSerializer):
    product_amount = serializers.SerializerMethodField()
    picked_ready = serializers.SerializerMethodField()

    def get_product_amount(self, obj):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        product_id = self.context.get('product_id', None)
        uom_id = self.context.get('uom_id', None)
        if tenant_id and company_id and product_id and uom_id and TypeCheck.check_uuid_list(
                [tenant_id, company_id, product_id, uom_id]
        ):
            return ProductWareHouse.get_stock(
                tenant_id=tenant_id, company_id=company_id,
                warehouse_id=obj.id, product_id=product_id,
                uom_id=uom_id
            )
        return 0

    def get_picked_ready(self, obj):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        product_id = self.context.get('product_id', None)
        uom_id = self.context.get('uom_id', None)
        if tenant_id and company_id and product_id and uom_id and TypeCheck.check_uuid_list(
                [tenant_id, company_id, product_id, uom_id]
        ):
            return ProductWareHouse.get_picked_ready(
                tenant_id=tenant_id, company_id=company_id,
                warehouse_id=obj.id, product_id=product_id,
                uom_id=uom_id
            )
        return 0

    class Meta:
        model = WareHouse
        fields = ('id', 'title', 'code', 'remarks', 'product_amount', 'picked_ready')
