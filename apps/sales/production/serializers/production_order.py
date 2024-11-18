from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.production.models import ProductionOrder, ProductionOrderTask
from apps.sales.production.serializers.production_order_sub import ProductionOrderSub, ProductionOrderValid
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel


# SUB
class POTaskCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = ProductionOrderTask
        fields = (
            'is_task',
            'task_title',
            'task_order',
            'product_id',
            'product_data',
            'uom_id',
            'uom_data',
            'quantity_bom',
            'quantity',
            'is_all_warehouse',
            'warehouse_id',
            'warehouse_data',
            'stock',
            'available',
            'tool_data',
            'order',
        )

    @classmethod
    def validate_product_id(cls, value):
        return ProductionOrderValid.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return ProductionOrderValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return ProductionOrderValid.validate_warehouse_id(value=value)


# PRODUCTION ORDER BEGIN
class ProductionOrderListSerializer(AbstractListSerializerModel):

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
            'status_production',
        )


class ProductionOrderDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
            'bom_data',
            'type_production',
            'product_data',
            'supplier_data',
            'purchase_order_data',
            'quantity',
            'uom_data',
            'warehouse_data',
            'sale_order_data',
            'status_production',
            'date_start',
            'date_end',
            'group_data',
            'time',
            'task_data',
            'date_created',
            'gr_remain_quantity',
        )


class ProductionOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    bom_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    purchase_order_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)
    group_id = serializers.UUIDField(required=False, allow_null=True)
    task_data = POTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = ProductionOrder
        fields = (
            'title',
            'bom_id',
            'bom_data',
            'type_production',
            'product_id',
            'product_data',
            'supplier_id',
            'supplier_data',
            'purchase_order_id',
            'purchase_order_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'sale_order_data',
            'status_production',
            'date_start',
            'date_end',
            'group_id',
            'group_data',
            'time',
            'task_data',
            'gr_remain_quantity',
        )

    @classmethod
    def validate_bom_id(cls, value):
        return ProductionOrderValid.validate_bom_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return ProductionOrderValid.validate_product_id(value=value)

    @classmethod
    def validate_supplier_id(cls, value):
        return ProductionOrderValid.validate_supplier_id(value=value)

    @classmethod
    def validate_purchase_order_id(cls, value):
        return ProductionOrderValid.validate_purchase_order_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return ProductionOrderValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return ProductionOrderValid.validate_warehouse_id(value=value)

    @classmethod
    def validate_group_id(cls, value):
        return ProductionOrderValid.validate_group_id(value=value)

    @decorator_run_workflow
    def create(self, validated_data):
        production_order = ProductionOrder.objects.create(**validated_data)
        ProductionOrderSub.create_sub_models(validated_data=validated_data, instance=production_order)
        return production_order


class ProductionOrderUpdateSerializer(AbstractCreateSerializerModel):
    bom_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    purchase_order_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)
    group_id = serializers.UUIDField(required=False, allow_null=True)
    task_data = POTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = ProductionOrder
        fields = (
            'title',
            'bom_id',
            'bom_data',
            'type_production',
            'product_id',
            'product_data',
            'supplier_id',
            'supplier_data',
            'purchase_order_id',
            'purchase_order_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'sale_order_data',
            'status_production',
            'date_start',
            'date_end',
            'group_id',
            'group_data',
            'time',
            'task_data',
            'gr_remain_quantity',
        )

    @classmethod
    def validate_bom_id(cls, value):
        return ProductionOrderValid.validate_bom_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return ProductionOrderValid.validate_product_id(value=value)

    @classmethod
    def validate_supplier_id(cls, value):
        return ProductionOrderValid.validate_supplier_id(value=value)

    @classmethod
    def validate_purchase_order_id(cls, value):
        return ProductionOrderValid.validate_purchase_order_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return ProductionOrderValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return ProductionOrderValid.validate_warehouse_id(value=value)

    @classmethod
    def validate_group_id(cls, value):
        return ProductionOrderValid.validate_group_id(value=value)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        ProductionOrderSub.create_sub_models(validated_data=validated_data, instance=instance)
        return instance


class ProductionOrderManualDoneSerializer(serializers.ModelSerializer):
    production_order_id = serializers.UUIDField()

    class Meta:
        model = ProductionOrder
        fields = (
            'production_order_id',
            'status_production',
        )

    def create(self, validated_data):
        production_order = ProductionOrder.objects.filter(id=validated_data.get('production_order_id', None)).first()
        if production_order:
            production_order.status_production = validated_data.get('status_production', 1)
            production_order.save(update_fields=['status_production'])
        return production_order
