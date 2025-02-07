from rest_framework import serializers

from apps.masterdata.saledata.models import WareHouse, ProductWareHouseSerial
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.inventory.models import RecoveryDelivery, RecoveryProduct, RecoveryWarehouse, RecoveryLeaseGenerate
from apps.sales.inventory.utils.logical_finish_recovery import RecoveryFinishHandler
from apps.sales.leaseorder.models import LeaseOrder
from apps.shared import AccountsMsg, ProductMsg, WarehouseMsg, SaleMsg


class RecoveryCommonCreate:

    @classmethod
    def create_recovery_delivery(cls, instance):
        keys_to_remove = ['id', 'remarks', 'agency', 'full_address', 'is_dropship']
        instance.recovery_delivery_recovery.all().delete()
        recovery_delivery_objs = RecoveryDelivery.objects.bulk_create(
            [RecoveryDelivery(
                goods_recovery=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **{k: v for k, v in recovery_delivery.items() if k not in keys_to_remove},
            ) for recovery_delivery in instance.recovery_delivery_data]
        )
        RecoveryCommonCreate.create_recovery_product(
            instance=instance, objs=recovery_delivery_objs, keys_to_remove=keys_to_remove
        )
        return True

    @classmethod
    def create_recovery_product(cls, instance, objs, keys_to_remove):
        for sub_delivery_obj in objs:
            recovery_products_objs = RecoveryProduct.objects.bulk_create(
                [RecoveryProduct(
                    goods_recovery=instance, recovery_delivery=sub_delivery_obj,
                    tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **{k: v for k, v in recovery_product.items() if k not in keys_to_remove},
                ) for recovery_product in sub_delivery_obj.delivery_product_data]
            )
            RecoveryCommonCreate.create_recovery_warehouse(
                instance=instance, objs=recovery_products_objs, keys_to_remove=keys_to_remove
            )
        return True

    @classmethod
    def create_recovery_warehouse(cls, instance, objs, keys_to_remove):
        for sub_product_obj in objs:
            recovery_warehouse_objs = RecoveryWarehouse.objects.bulk_create(
                [RecoveryWarehouse(
                    goods_recovery=instance, recovery_product=sub_product_obj,
                    tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **{k: v for k, v in recovery_warehouse.items() if k not in keys_to_remove},
                ) for recovery_warehouse in sub_product_obj.product_warehouse_data]
            )
            RecoveryCommonCreate.create_recovery_lease_generate(
                instance=instance, objs=recovery_warehouse_objs, keys_to_remove=keys_to_remove
            )
        return True

    @classmethod
    def create_recovery_lease_generate(cls, instance, objs, keys_to_remove):
        for sub_warehouse_obj in objs:
            RecoveryLeaseGenerate.objects.bulk_create(
                [RecoveryLeaseGenerate(
                    goods_recovery=instance, recovery_warehouse=sub_warehouse_obj,
                    tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **{k: v for k, v in recovery_lease_generate.items() if k not in keys_to_remove},
                ) for recovery_lease_generate in sub_warehouse_obj.lease_generate_data]
            )
        return True

    @classmethod
    def create_sub_models(cls, instance):
        cls.create_recovery_delivery(instance=instance)

        RecoveryFinishHandler.clone_lease_product(instance=instance)
        return True


class RecoveryCommonValidate:

    @classmethod
    def validate_customer_id(cls, value):
        try:
            return str(Account.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_lease_order_id(cls, value):
        try:
            return str(LeaseOrder.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except LeaseOrder.DoesNotExist:
            raise serializers.ValidationError({'lease_order': SaleMsg.LEASE_ORDER_NOT_EXIST})

    @classmethod
    def validate_delivery_id(cls, value):
        try:
            return str(OrderDeliverySub.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except OrderDeliverySub.DoesNotExist:
            raise serializers.ValidationError({'delivery': SaleMsg.DELIVERY_NOT_EXIST})

    @classmethod
    def validate_product_id(cls, value):
        try:
            return str(Product.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_uom_id(cls, value):
        try:
            return str(UnitOfMeasure.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})

    @classmethod
    def validate_tax_id(cls, value):
        try:
            return str(Tax.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': ProductMsg.TAX_DOES_NOT_EXIST})

    @classmethod
    def validate_warehouse_id(cls, value):
        try:
            return str(WareHouse.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': WarehouseMsg.WAREHOUSE_NOT_EXIST})

    @classmethod
    def validate_serial_id(cls, value):
        try:
            return str(ProductWareHouseSerial.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except ProductWareHouseSerial.DoesNotExist:
            raise serializers.ValidationError({'serial': WarehouseMsg.SERIAL_NOT_EXIST})


# SUB SERIALIZERS
class RecoveryLeaseGenerateSerializer(serializers.ModelSerializer):
    serial_id = serializers.UUIDField()

    class Meta:
        model = RecoveryLeaseGenerate
        fields = (
            'serial_id',
            'serial_data',
            'remark',
        )

    @classmethod
    def validate_serial_id(cls, value):
        return RecoveryCommonValidate().validate_serial_id(value=value)


class RecoveryWarehouseSerializer(serializers.ModelSerializer):
    warehouse_id = serializers.UUIDField()
    lease_generate_data = RecoveryLeaseGenerateSerializer(many=True, required=False)

    class Meta:
        model = RecoveryWarehouse
        fields = (
            'title',
            'code',
            'warehouse_id',
            'warehouse_data',
            'quantity_recovery',

            'lease_generate_data',
        )

    @classmethod
    def validate_warehouse_id(cls, value):
        return RecoveryCommonValidate().validate_warehouse_id(value=value)


class RecoveryProductSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()
    offset_id = serializers.UUIDField()
    uom_id = serializers.UUIDField()
    uom_time_id = serializers.UUIDField(required=False)
    product_depreciation_start_date = serializers.CharField()
    product_depreciation_end_date = serializers.CharField()
    product_warehouse_data = RecoveryWarehouseSerializer(many=True, required=False)

    class Meta:
        model = RecoveryProduct
        fields = (
            'product_id',
            'product_data',
            'asset_type',
            'offset_id',
            'offset_data',
            'uom_id',
            'uom_data',
            'uom_time_id',
            'uom_time_data',
            'product_quantity',
            'product_quantity_time',
            'product_unit_price',
            'product_subtotal_price',
            'quantity_ordered',
            'quantity_delivered',
            'quantity_recovered',
            'quantity_recovery',
            'delivery_data',

            'product_warehouse_data',
            # Depreciation fields

            'product_depreciation_subtotal',
            'product_depreciation_price',
            'product_depreciation_method',
            'product_depreciation_adjustment',
            'product_depreciation_time',
            'product_depreciation_start_date',
            'product_depreciation_end_date',
        )

    @classmethod
    def validate_product_id(cls, value):
        return RecoveryCommonValidate().validate_product_id(value=value)

    @classmethod
    def validate_offset_id(cls, value):
        return RecoveryCommonValidate().validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return RecoveryCommonValidate().validate_uom_id(value=value)

    @classmethod
    def validate_uom_time_id(cls, value):
        return RecoveryCommonValidate().validate_uom_id(value=value)


class RecoveryDeliverySerializer(serializers.ModelSerializer):
    delivery_id = serializers.UUIDField()
    delivery_product_data = RecoveryProductSerializer(many=True, required=False)

    class Meta:
        model = RecoveryDelivery
        fields = (
            'delivery_id',
            'delivery_data',
            'delivery_product_data',
        )

    @classmethod
    def validate_delivery_id(cls, value):
        return RecoveryCommonValidate().validate_delivery_id(value=value)
