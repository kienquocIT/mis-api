from rest_framework import serializers

from apps.core.hr.models import Group
from apps.masterdata.saledata.models import Product, UnitOfMeasure, WareHouse, Account
from apps.sales.production.models import ProductionOrderTask, ProductionOrderTaskTool, ProductionOrderSaleOrder, BOM
from apps.sales.purchasing.models import PurchaseOrder
from apps.shared import SaleMsg, PurchasingMsg, AccountsMsg


class ProductionOrderSub:

    @classmethod
    def create_sub(cls, validated_data, instance):
        instance.production_sale_order_production.all().delete()
        ProductionOrderSaleOrder.objects.bulk_create([ProductionOrderSaleOrder(
            production_order=instance, sale_order_id=sale_order_data.get('id', None)
        ) for sale_order_data in instance.sale_order_data])
        instance.po_task_production_order.all().delete()
        tasks = ProductionOrderTask.objects.bulk_create([
            ProductionOrderTask(
                production_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **task_data
            ) for task_data in validated_data['task_data']
        ])
        for task in tasks:
            if task.is_task is True:
                task.po_task_tool_task.all().delete()
                ProductionOrderTaskTool.objects.bulk_create([ProductionOrderTaskTool(
                    po_task=task, tool_id=tool_data.get('id', None)
                ) for tool_data in task.tool_data])
        return True

    @classmethod
    def create_sub_models(cls, validated_data, instance):
        cls.create_sub(validated_data=validated_data, instance=instance)
        return True


class ProductionOrderValid:

    @classmethod
    def validate_bom_id(cls, value):
        try:
            return str(BOM.objects.get(id=value).id)
        except BOM.DoesNotExist:
            raise serializers.ValidationError({'bom': SaleMsg.BOM_NOT_EXIST})

    @classmethod
    def validate_product_id(cls, value):
        try:
            if value is None:
                return value
            return str(Product.objects.get(id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': SaleMsg.PRODUCT_NOT_EXIST})

    @classmethod
    def validate_supplier_id(cls, value):
        try:
            if value is None:
                return value
            return str(Account.objects.get(id=value).id)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'supplier': AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_purchase_order_id(cls, value):
        try:
            if value is None:
                return value
            return str(PurchaseOrder.objects.get(id=value).id)
        except PurchaseOrder.DoesNotExist:
            raise serializers.ValidationError({'purchase order': PurchasingMsg.PURCHASE_ORDER_NOT_EXIST})

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
