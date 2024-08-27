# from rest_framework import serializers

from apps.sales.production.models import ProductionOrderTask, ProductionOrderTaskTool, ProductionOrderSaleOrder


class ProductionOrderSub:

    @classmethod
    def create_sub(cls, validated_data, instance):
        instance.production_sale_order_production.all().delete()
        ProductionOrderSaleOrder.objects.bulk_create([ProductionOrderSaleOrder(
            production_order=instance, sale_order=sale_order_data.get('id', None)
        ) for sale_order_data in instance.sale_order_data])
        instance.po_task_production_order.all().delete()
        tasks = ProductionOrderTask.objects.bulk_create([
            ProductionOrderTask(
                production_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **task_data
            ) for task_data in validated_data['task_data']
        ])
        for task in tasks:
            task.po_task_tool_task.all().delete()
            ProductionOrderTaskTool.objects.bulk_create([ProductionOrderTaskTool(
                po_task=task, tool_id=tool_data.get('id', None)
            ) for tool_data in task.tool_data])
        return True

    @classmethod
    def delete_old_task(cls, instance):
        instance.po_task_production_order.all().delete()
        return True

    @classmethod
    def create_sub_models(cls, validated_data, instance, is_update=False):
        # if 'task_data' in validated_data:
        #     if is_update is True:
        #         cls.delete_old_task(instance=instance)
        cls.create_sub(validated_data=validated_data, instance=instance)
        return True
