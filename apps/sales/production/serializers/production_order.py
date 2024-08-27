from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.production.models import ProductionOrder, ProductionOrderTask
from apps.sales.production.serializers.production_order_sub import ProductionOrderSub
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel


# SUB
class POTaskCreateSerializer(serializers.ModelSerializer):

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
            'warehouse_id',
            'warehouse_data',
            'stock',
            'available',
            'tool',
            'order',
        )


# PRODUCTION ORDER BEGIN
class ProductionOrderListSerializer(AbstractListSerializerModel):

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
        )


class ProductionOrderDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
            'task_data',
        )


class ProductionOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField()
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
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'sale_order',
            'sale_order_data',
            'status_production',
            'date_start',
            'date_end',
            'group_id',
            'group_data',
            'time',
            'task_data',
        )

    @decorator_run_workflow
    def create(self, validated_data):
        production_order = ProductionOrder.objects.create(**validated_data)
        ProductionOrderSub.create_sub_models(validated_data=validated_data, instance=production_order)
        return production_order


class ProductionOrderUpdateSerializer(AbstractCreateSerializerModel):
    task_data = POTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = ProductionOrder
        fields = (
            'title',
            'task_data',
        )

    # @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        ProductionOrderSub.create_sub_models(validated_data=validated_data, instance=instance, is_update=True)
        return instance
