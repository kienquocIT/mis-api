from rest_framework import serializers

from apps.core.hr.models import Group, Employee
from apps.masterdata.saledata.models import Product, UnitOfMeasure, WareHouse
from apps.sales.opportunity.models import Opportunity
from apps.sales.production.models import WorkOrderTask, WorkOrderTaskTool, BOM
from apps.shared import SaleMsg


class WorkOrderSub:

    @classmethod
    def create_sub(cls, validated_data, instance):
        instance.wo_task_work_order.all().delete()
        tasks = WorkOrderTask.objects.bulk_create([
            WorkOrderTask(
                work_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **task_data
            ) for task_data in validated_data['task_data']
        ])
        for task in tasks:
            if task.is_task is True:
                task.wo_task_tool_task.all().delete()
                WorkOrderTaskTool.objects.bulk_create([WorkOrderTaskTool(
                    wo_task=task, tool_id=tool_data.get('id', None)
                ) for tool_data in task.tool_data])
        return True

    @classmethod
    def create_sub_models(cls, validated_data, instance):
        cls.create_sub(validated_data=validated_data, instance=instance)
        return True


class WorkOrderValid:

    @classmethod
    def validate_bom_id(cls, value):
        try:
            return str(BOM.objects.get(id=value).id)
        except BOM.DoesNotExist:
            raise serializers.ValidationError({'bom': SaleMsg.BOM_NOT_EXIST})

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            return str(Opportunity.objects.get(id=value).id)
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': SaleMsg.OPPORTUNITY_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return str(Employee.objects.get(id=value).id)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee': SaleMsg.EMPLOYEE_INHERIT_NOT_EXIST})

    @classmethod
    def validate_product_id(cls, value):
        try:
            if value is None:
                return value
            return str(Product.objects.get(id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': SaleMsg.PRODUCT_NOT_EXIST})

    @classmethod
    def validate_uom_id(cls, value):
        try:
            if value is None:
                return value
            return str(UnitOfMeasure.objects.get(id=value).id)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': SaleMsg.UOM_NOT_EXIST})

    @classmethod
    def validate_warehouse_id(cls, value):
        try:
            if value is None:
                return value
            return str(WareHouse.objects.get(id=value).id)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': SaleMsg.WAREHOUSE_NOT_EXIST})

    @classmethod
    def validate_group_id(cls, value):
        try:
            if value is None:
                return value
            return str(Group.objects.get(id=value).id)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'group': SaleMsg.GROUP_NOT_EXIST})
