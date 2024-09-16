from rest_framework import serializers

from apps.masterdata.saledata.models import Product, UnitOfMeasure, WareHouse
from apps.sales.production.models import ProductionReportTask, ProductionOrder
from apps.shared import SaleMsg


class ProductionReportSub:

    @classmethod
    def create_sub(cls, validated_data, instance):
        instance.pr_task_production_report.all().delete()
        ProductionReportTask.objects.bulk_create([
            ProductionReportTask(
                production_report=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **task_data
            ) for task_data in validated_data['task_data']
        ])
        return True

    @classmethod
    def create_sub_models(cls, validated_data, instance):
        cls.create_sub(validated_data=validated_data, instance=instance)
        return True


class ProductionReportValid:

    @classmethod
    def validate_production_order_id(cls, value):
        try:
            return str(ProductionOrder.objects.get(id=value).id)
        except ProductionOrder.DoesNotExist:
            raise serializers.ValidationError({'production order': SaleMsg.PRODUCTION_ORDER_NOT_EXIST})

    @classmethod
    def validate_product_id(cls, value):
        try:
            return str(Product.objects.get(id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': SaleMsg.PRODUCT_NOT_EXIST})

    @classmethod
    def validate_uom_id(cls, value):
        try:
            return str(UnitOfMeasure.objects.get(id=value).id)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'uom': SaleMsg.UOM_NOT_EXIST})

    @classmethod
    def validate_warehouse_id(cls, value):
        try:
            return str(WareHouse.objects.get(id=value).id)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': SaleMsg.WAREHOUSE_NOT_EXIST})
