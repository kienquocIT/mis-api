from rest_framework import serializers

from apps.masterdata.saledata.models import (
    WareHouse, ProductWareHouse,
)

__all__ = [
    'WareHouseListSerializer',
    'WareHouseCreateSerializer',
    'WareHouseDetailSerializer',
    'WareHouseUpdateSerializer',
    'ProductWareHouseStockListSerializer',
    'ProductWareHouseListSerializer',
    'WareHouseListSerializerForInventoryAdjustment',
]

from apps.shared import TypeCheck


class WareHouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = (
            'id',
            'title',
            'code',
            'remarks',
            'is_active',
        )


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


class ProductWareHouseStockListSerializer(serializers.ModelSerializer):
    product_amount = serializers.SerializerMethodField()
    picked_ready = serializers.SerializerMethodField()
    warehouse_uom = serializers.SerializerMethodField()
    original_info = serializers.SerializerMethodField()

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

    def get_warehouse_uom(self, obj):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        if tenant_id and company_id and TypeCheck.check_uuid_list(
                [tenant_id, company_id]
        ):
            record = ProductWareHouse.objects.filter_current(
                tenant_id=tenant_id, company_id=company_id,
                warehouse_id=obj.id
            )
            return {
                'id': str(record.first().uom_id),
                'ratio': record.first().uom.ratio,
                'rounding': record.first().uom.rounding,
                'title': record.first().uom.title
            }
        return {}

    def get_original_info(self, obj):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        product_id = self.context.get('product_id', None)
        temp = {
            'stock_amount': 0,
            'sold_amount': 0,
            'picked_ready': 0
        }
        if tenant_id and company_id and product_id and TypeCheck.check_uuid_list(
                [tenant_id, company_id, product_id]
        ):
            records = ProductWareHouse.objects.filter_current(
                tenant_id=tenant_id, company_id=company_id,
                warehouse_id=obj.id, product_id=product_id
            )
            if records.exists():
                record = records.first()
                return {
                    'stock_amount': record.stock_amount,
                    'sold_amount': record.sold_amount,
                    'picked_ready': record.picked_ready
                }
        return temp

    class Meta:
        model = WareHouse
        fields = ('id', 'title', 'code', 'remarks', 'product_amount', 'picked_ready', 'warehouse_uom',
                  'original_info')


class ProductWareHouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = '__all__'


class WareHouseListSerializerForInventoryAdjustment(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = WareHouse
        fields = (
            'id',
            'title',
            'code',
            'remarks',
            'is_active',
            'product_list'
        )

    @classmethod
    def get_product_list(cls, obj):
        results = []
        for item in obj.products.all():
            results.append({
                'id': str(item.id),
                'title': item.title,
                'inventory_uom': {
                    'id': item.inventory_uom_id,
                    'code': item.inventory_uom.code,
                    'title': item.inventory_uom.title
                } if item.inventory_uom else {}
            })
        return results
