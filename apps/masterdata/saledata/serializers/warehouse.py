from rest_framework import serializers

from apps.masterdata.saledata.models import (
    WareHouse, ProductWareHouse, Account,
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

from apps.shared import TypeCheck, WarehouseMsg


class WareHouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouse
        fields = (
            'id',
            'title',
            'code',
            'remarks',
            'is_active',
            'agency'
        )


class WareHouseCreateSerializer(serializers.ModelSerializer):
    agency = serializers.UUIDField(required=False)

    class Meta:
        model = WareHouse
        fields = (
            'title',
            'remarks',
            'is_active',
            'city',
            'district',
            'ward',
            'address',
            'agency',
            'full_address',
            'warehouse_type',
        )

    @classmethod
    def validate_agency(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except Account.DoesNotExist:
                raise serializers.ValidationError({'agency': WarehouseMsg.AGENCY_NOT_EXIST})
        return None


class WareHouseDetailSerializer(serializers.ModelSerializer):
    agency = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()

    class Meta:
        model = WareHouse
        fields = (
            'id',
            'title',
            'code',
            'remarks',
            'address',
            'is_active',
            'full_address',
            'city',
            'ward',
            'district',
            'warehouse_type',
            'agency',
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
    def get_city(cls, obj):
        if obj.city:
            return {
                'id': obj.city_id,
                'title': obj.city.title,
            }
        return {}

    @classmethod
    def get_district(cls, obj):
        if obj.district:
            return {
                'id': obj.district_id,
                'title': obj.district.title,
            }
        return {}

    @classmethod
    def get_ward(cls, obj):
        if obj.ward:
            return {
                'id': obj.ward_id,
                'title': obj.ward.title,
            }
        return {}


class WareHouseUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, required=False)
    remarks = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    agency = serializers.UUIDField(required=False, allow_null=True)
    city = serializers.UUIDField(required=False)
    district = serializers.UUIDField(required=False)
    ward = serializers.UUIDField(required=False)
    address = serializers.CharField(required=False)
    full_address = serializers.CharField(required=False)

    class Meta:
        model = WareHouse
        fields = (
            'title',
            'remarks',
            'is_active',
            'city',
            'district',
            'ward',
            'address',
            'agency',
            'full_address',
            'warehouse_type',
        )

    @classmethod
    def validate_agency(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except Account.DoesNotExist:
                raise serializers.ValidationError({'agency': WarehouseMsg.AGENCY_NOT_EXIST})
        return None


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
    agency = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = '__all__'

    @classmethod
    def get_agency(cls, obj):
        return obj.warehouse.agency_id


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
