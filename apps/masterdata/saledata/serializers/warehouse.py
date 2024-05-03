from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import (
    WareHouse, ProductWareHouse, Account, ProductWareHouseLot, ProductWareHouseSerial,
    WarehouseEmployeeConfig, WarehouseEmployeeConfigDetail
)

__all__ = [
    'WareHouseListSerializer',
    'WareHouseCreateSerializer',
    'WareHouseDetailSerializer',
    'WareHouseUpdateSerializer',
    'ProductWareHouseStockListSerializer',
    'ProductWareHouseListSerializer',
    'WareHouseListSerializerForInventoryAdjustment',
    'ProductWarehouseLotListSerializer',
    'ProductWarehouseSerialListSerializer',
    'ProductWarehouseAssetToolsListSerializer',
    'WarehouseEmployeeConfigListSerializer',
    'WarehouseEmployeeConfigCreateSerializer',
    'WarehouseEmployeeConfigDetailSerializer'
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
            'agency',
            'full_address'
        )


class WareHouseCreateSerializer(serializers.ModelSerializer):
    agency = serializers.UUIDField(required=False, allow_null=True)

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
            'is_dropship'
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
            'is_dropship'
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
    agency = serializers.UUIDField(required=False, allow_null=True)

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
            'is_dropship'
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
            product_warehouse = ProductWareHouse.objects.filter(
                tenant_id=tenant_id, company_id=company_id,
                warehouse_id=obj.id, product_id=product_id,
            ).first()
            if product_warehouse:
                return product_warehouse.stock_amount
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
        product_id = self.context.get('product_id', None)
        if tenant_id and company_id and TypeCheck.check_uuid_list(
                [tenant_id, company_id]
        ):
            record = ProductWareHouse.objects.filter_current(
                tenant_id=tenant_id, company_id=company_id,
                warehouse_id=obj.id, product_id=product_id
            )
            if record.exists():
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
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    agency = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'product',
            'warehouse',
            'uom',
            'stock_amount',
            'receipt_amount',
            'sold_amount',
            'picked_ready',
            'agency',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
        } if obj.product else {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
            'ratio': obj.uom.ratio
        } if obj.uom else {}

    @classmethod
    def get_agency(cls, obj):
        return obj.warehouse.agency_id


class ProductWareHouseListSerializerForGoodsTransfer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    serial_detail = serializers.SerializerMethodField()
    lot_detail = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'product',
            'warehouse',
            'uom',
            'stock_amount',
            'receipt_amount',
            'sold_amount',
            'picked_ready',
            'serial_detail',
            'lot_detail',
            'unit_cost'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_traceability_method': obj.product.general_traceability_method,
        } if obj.product else {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
            'ratio': obj.uom.ratio
        } if obj.uom else {}

    @classmethod
    def get_serial_detail(cls, obj):
        return [{
            'id': serial.id,
            'vendor_serial_number': serial.vendor_serial_number,
            'serial_number': serial.serial_number,
            'expire_date': serial.expire_date,
            'manufacture_date': serial.manufacture_date,
            'warranty_start': serial.warranty_start,
            'warranty_end': serial.warranty_end
        } for serial in obj.product_warehouse_serial_product_warehouse.filter(
            is_delete=False
        ).order_by('vendor_serial_number', 'serial_number')]

    @classmethod
    def get_lot_detail(cls, obj):
        return [{
            'id': lot.id,
            'lot_number': lot.lot_number,
            'quantity_import': lot.quantity_import,
            'expire_date': lot.expire_date,
            'manufacture_date': lot.manufacture_date
        } for lot in obj.product_warehouse_lot_product_warehouse.filter(quantity_import__gt=0).order_by('lot_number')]

    @classmethod
    def get_unit_cost(cls, obj):
        return obj.product.get_unit_cost_by_warehouse(obj.warehouse_id)


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
        products = ProductWareHouse.objects.filter(warehouse=obj)
        for item in products:
            results.append(
                {
                    'id': str(item.id),
                    'product': {
                        'id': item.product_id,
                        'code': item.product.code,
                        'title': item.product.title
                    },
                    'available_amount': item.stock_amount,
                    'inventory_uom': item.uom_data,
                }
            )
        return results


class ProductWarehouseLotListSerializer(serializers.ModelSerializer):
    product_warehouse = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouseLot
        fields = (
            'id',
            'product_warehouse',
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date',
        )

    @classmethod
    def get_product_warehouse(cls, obj):
        return {
            'id': obj.product_warehouse_id,
            'product': {
                'id': obj.product_warehouse.product_id,
                'title': obj.product_warehouse.product.title,
                'code': obj.product_warehouse.product.code,
                'uom_inventory': {
                    'id': obj.product_warehouse.product.inventory_uom_id,
                    'title': obj.product_warehouse.product.inventory_uom.title,
                    'code': obj.product_warehouse.product.inventory_uom.code,
                    'ratio': obj.product_warehouse.product.inventory_uom.ratio,
                } if obj.product_warehouse.product.inventory_uom else {},
            } if obj.product_warehouse.product else {},
            'warehouse': {
                'id': obj.product_warehouse.warehouse_id,
                'title': obj.product_warehouse.warehouse.title,
                'code': obj.product_warehouse.warehouse.code,
            } if obj.product_warehouse.warehouse else {},
            'uom': {
                'id': obj.product_warehouse.uom_id,
                'title': obj.product_warehouse.uom.title,
                'code': obj.product_warehouse.uom.code,
                'ratio': obj.product_warehouse.uom.ratio,
            } if obj.product_warehouse.uom else {}
        }


class ProductWarehouseSerialListSerializer(serializers.ModelSerializer):
    product_warehouse = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouseSerial
        fields = (
            'id',
            'product_warehouse',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
            'is_delete'
        )

    @classmethod
    def get_product_warehouse(cls, obj):
        return {
            'id': obj.product_warehouse_id,
            'product': {
                'id': obj.product_warehouse.product_id,
                'title': obj.product_warehouse.product.title,
                'code': obj.product_warehouse.product.code,
            } if obj.product_warehouse.product else {},
            'warehouse': {
                'id': obj.product_warehouse.warehouse_id,
                'title': obj.product_warehouse.warehouse.title,
                'code': obj.product_warehouse.warehouse.code,
            } if obj.product_warehouse.warehouse else {},
        }


class ProductWarehouseAssetToolsListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'product',
            'uom',
            'warehouse',
            'stock_amount',
            'used_amount',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
        } if obj.product else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            'id': obj.uom_id,
            'title': obj.uom.title,
            'code': obj.uom.code,
        } if obj.uom else {}

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
        } if obj.warehouse else {}


class WarehouseEmployeeConfigListSerializer(serializers.ModelSerializer):
    warehouse_list = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseEmployeeConfig
        fields = (
            'id',
            'warehouse_list',
            'employee'
        )

    @classmethod
    def get_employee(cls, obj):
        return {
            'id': obj.employee_id,
            'fullname': obj.employee.get_full_name(2),
            'code': obj.employee.code
        }

    @classmethod
    def get_warehouse_list(cls, obj):
        return sorted([{
            'id': cf_obj.warehouse_id,
            'title': cf_obj.warehouse.title,
            'code': cf_obj.warehouse.code
        } for cf_obj in obj.wh_emp_config_detail_cf.all()], key=lambda key: key['code'])


class WarehouseEmployeeConfigCreateSerializer(serializers.ModelSerializer):
    employee = serializers.UUIDField(required=True)
    warehouse_list = serializers.ListField(required=True, help_text="List of Warehouse id")

    class Meta:
        model = WarehouseEmployeeConfig
        fields = (
            'warehouse_list',
            'employee'
        )

    @classmethod
    def validate_employee(cls, attr):
        if not attr:
            raise serializers.ValidationError({'Employee': 'Employee can not be null.'})
        return Employee.objects.get(id=attr)

    @classmethod
    def validate_warehouse_list(cls, attr):
        if len(attr) == 0:
            raise serializers.ValidationError({'Warehouse list': 'Please select at least 1 warehouse.'})
        return attr

    def create(self, validated_data):
        if hasattr(validated_data['employee'], 'warehouse_employees_emp'):
            validated_data['employee'].warehouse_employees_emp.delete()
        config = WarehouseEmployeeConfig.objects.create(**validated_data)
        bulk_info = []
        for wh_id in config.warehouse_list:
            bulk_info.append(WarehouseEmployeeConfigDetail(config=config, warehouse_id=wh_id))
        WarehouseEmployeeConfigDetail.objects.bulk_create(bulk_info)
        return config


class WarehouseEmployeeConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseEmployeeConfig
        fields = (
            'id',
            'warehouse_list',
            'employee'
        )
