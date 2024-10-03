from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.production.models import WorkOrder, WorkOrderTask
from apps.sales.production.serializers.work_order_sub import WorkOrderSub, WorkOrderValid
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel


# SUB
class WOTaskCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = WorkOrderTask
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
        return WorkOrderValid.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return WorkOrderValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return WorkOrderValid.validate_warehouse_id(value=value)


# WORK ORDER BEGIN
class WorkOrderListSerializer(AbstractListSerializerModel):

    class Meta:
        model = WorkOrder
        fields = (
            'id',
            'title',
            'code',
            'status_production',
        )


class WorkOrderDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = WorkOrder
        fields = (
            'id',
            'title',
            'code',
            'bom_data',
            'opportunity_data',
            'employee_inherit_data',
            'sale_order_data',
            'product_data',
            'quantity',
            'uom_data',
            'warehouse_data',
            'status_production',
            'date_start',
            'date_end',
            'group_data',
            'time',
            'task_data',
            'date_created',
            'gr_remain_quantity',
        )


class WorkOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    bom_id = serializers.UUIDField(required=False, allow_null=True)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    sale_order_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)
    group_id = serializers.UUIDField(required=False, allow_null=True)
    task_data = WOTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = WorkOrder
        fields = (
            'title',
            'bom_id',
            'bom_data',
            'opportunity_id',
            'opportunity_data',
            'employee_inherit_id',
            'employee_inherit_data',
            'product_id',
            'product_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'sale_order_id',
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
        return WorkOrderValid.validate_bom_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return WorkOrderValid.validate_opportunity_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return WorkOrderValid.validate_employee_inherit_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return WorkOrderValid.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return WorkOrderValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return WorkOrderValid.validate_warehouse_id(value=value)

    @classmethod
    def validate_group_id(cls, value):
        return WorkOrderValid.validate_group_id(value=value)

    @decorator_run_workflow
    def create(self, validated_data):
        work_order = WorkOrder.objects.create(**validated_data)
        WorkOrderSub.create_sub_models(validated_data=validated_data, instance=work_order)
        return work_order


class WorkOrderUpdateSerializer(AbstractCreateSerializerModel):
    bom_id = serializers.UUIDField(required=False, allow_null=True)
    opportunity_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    sale_order_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)
    group_id = serializers.UUIDField(required=False, allow_null=True)
    task_data = WOTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = WorkOrder
        fields = (
            'title',
            'bom_id',
            'bom_data',
            'opportunity_id',
            'opportunity_data',
            'employee_inherit_id',
            'employee_inherit_data',
            'product_id',
            'product_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'sale_order_id',
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
        return WorkOrderValid.validate_bom_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return WorkOrderValid.validate_opportunity_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return WorkOrderValid.validate_employee_inherit_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return WorkOrderValid.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return WorkOrderValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return WorkOrderValid.validate_warehouse_id(value=value)

    @classmethod
    def validate_group_id(cls, value):
        return WorkOrderValid.validate_group_id(value=value)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        WorkOrderSub.create_sub_models(validated_data=validated_data, instance=instance)
        return instance


class WorkOrderManualDoneSerializer(serializers.ModelSerializer):
    work_order_id = serializers.UUIDField()

    class Meta:
        model = WorkOrder
        fields = (
            'work_order_id',
            'status_production',
        )

    def create(self, validated_data):
        work_order = WorkOrder.objects.filter(id=validated_data.get('work_order_id', None)).first()
        if work_order:
            work_order.status_production = validated_data.get('status_production', 1)
            work_order.save(update_fields=['status_production'])
        return work_order
