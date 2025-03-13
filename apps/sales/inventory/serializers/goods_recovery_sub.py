from rest_framework import serializers

from apps.masterdata.saledata.models import WareHouse, ProductWareHouseSerial
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.price import Tax
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.inventory.models import RecoveryDelivery, RecoveryProduct, RecoveryProductAsset
from apps.sales.leaseorder.models import LeaseOrder
from apps.shared import AccountsMsg, ProductMsg, WarehouseMsg, SaleMsg


class RecoveryCommonCreate:

    @classmethod
    def create_recovery_delivery(cls, instance):
        keys_to_remove = [
            'id', 'remarks',
            'agency', 'full_address',
            'is_dropship', 'quantity_delivered',
            'picked_quantity', 'quantity_remain_recovery',
        ]
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
            for recovery_product_obj in recovery_products_objs:
                RecoveryProductAsset.objects.bulk_create([RecoveryProductAsset(
                    goods_recovery=instance, recovery_product=recovery_product_obj,
                    tenant_id=instance.tenant_id, company_id=instance.company_id,
                    **asset_data,
                ) for asset_data in recovery_product_obj.asset_data])
        return True

    @classmethod
    def create_sub_models(cls, instance):
        cls.create_recovery_delivery(instance=instance)
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
            if value is None:
                return value
            return str(Product.objects.get_current(fill__tenant=True, fill__company=True, id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_uom_id(cls, value):
        try:
            if value is None:
                return value
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
class RecoveryProductSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()
    offset_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    uom_time_id = serializers.UUIDField(required=False, allow_null=True)

    quantity_delivered = serializers.FloatField(default=0)
    quantity_remain_recovery = serializers.FloatField(default=0)

    class Meta:
        model = RecoveryProduct
        fields = (
            'product_id',
            'product_data',
            'asset_type',
            'offset_id',
            'offset_data',
            'asset_data',
            'uom_id',
            'uom_data',
            'uom_time_id',
            'uom_time_data',
            'product_quantity',
            'product_quantity_time',
            'product_cost',
            'product_subtotal_cost',
            'quantity_delivered',
            'quantity_remain_recovery',
            'quantity_recovery',
            'delivery_data',
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
