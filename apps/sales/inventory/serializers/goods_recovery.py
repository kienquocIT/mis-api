from rest_framework import serializers

# from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.inventory.models import GoodsRecovery
from apps.sales.inventory.serializers.goods_recovery_sub import RecoveryCommonCreate, RecoveryCommonValidate
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel


# GOODS RECOVERY BEGIN
class GoodsRecoveryListSerializer(AbstractListSerializerModel):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = GoodsRecovery
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'date_created',
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}


class GoodsRecoveryMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsRecovery
        fields = (
            'id',
            'title',
            'code',
            'date_created',
        )


class GoodsRecoveryDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = GoodsRecovery
        fields = (
            'id',
            'title',
            'code',
            'customer_data',
            'lease_order_data',
            'recovery_delivery_data',
        )


class GoodsRecoveryCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    lease_order_id = serializers.UUIDField()

    class Meta:
        model = GoodsRecovery
        fields = (
            'title',
            'code',
            'date_recovery',
            'status_recovery',
            'customer_id',
            'customer_data',
            'lease_order_id',
            'lease_order_data',
            'recovery_delivery_data',
            # attachment
            # 'attachment',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return RecoveryCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_lease_order_id(cls, value):
        return RecoveryCommonValidate().validate_lease_order_id(value=value)

    # @decorator_run_workflow
    def create(self, validated_data):
        goods_recovery = GoodsRecovery.objects.create(**validated_data)
        RecoveryCommonCreate().create_sub_models(instance=goods_recovery)

        return goods_recovery


class GoodsRecoveryUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    lease_order_id = serializers.UUIDField()

    class Meta:
        model = GoodsRecovery
        fields = (
            'title',
            'code',
            'customer_id',
            'customer_data',
            'lease_order_id',
            'lease_order_data',
            'recovery_delivery_data',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return RecoveryCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_lease_order_id(cls, value):
        return RecoveryCommonValidate().validate_lease_order_id(value=value)

    # @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        RecoveryCommonCreate().create_sub_models(instance=instance)
        return instance
