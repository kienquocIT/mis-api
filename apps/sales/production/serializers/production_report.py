from rest_framework import serializers

from apps.sales.production.models import ProductionReportTask, ProductionReport
from apps.sales.production.serializers.production_report_sub import ProductionReportValid, ProductionReportSub


# SUB
class PRTaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductionReportTask
        fields = (
            'is_task',
            'task_title',
            'task_order',
            'product_id',
            'product_data',
            'uom_id',
            'uom_data',
            'quantity',
            'quantity_actual',
            'order',
        )


# PRODUCTION REPORT BEGIN
class ProductionReportListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductionReport
        fields = (
            'id',
            'title',
            'code',
        )


class ProductionReportDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductionReport
        fields = (
            'id',
            'title',
            'code',
            'production_order_data',
            'product_data',
            'quantity',
            'uom_data',
            'warehouse_data',
            'quantity_finished',
            'quantity_ng',
            'task_data',
            'date_created',
        )


class ProductionReportCreateSerializer(serializers.ModelSerializer):
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)
    task_data = PRTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = ProductionReport
        fields = (
            'title',
            'production_order_id',
            'production_order_data',
            'product_id',
            'product_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'quantity_finished',
            'quantity_ng',
            'task_data',
            'gr_remain_quantity',
        )

    @classmethod
    def validate_production_order_id(cls, value):
        return ProductionReportValid.validate_production_order_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return ProductionReportValid.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return ProductionReportValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return ProductionReportValid.validate_warehouse_id(value=value)

    def create(self, validated_data):
        production_report = ProductionReport.objects.create(**validated_data)
        ProductionReportSub.create_sub_models(validated_data=validated_data, instance=production_report)
        return production_report


class ProductionReportUpdateSerializer(serializers.ModelSerializer):
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    uom_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)
    task_data = PRTaskCreateSerializer(many=True, required=False)

    class Meta:
        model = ProductionReport
        fields = (
            'title',
            'production_order_id',
            'production_order_data',
            'product_id',
            'product_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_id',
            'warehouse_data',
            'quantity_finished',
            'quantity_ng',
            'task_data',
            'gr_remain_quantity',
        )

    @classmethod
    def validate_production_order_id(cls, value):
        return ProductionReportValid.validate_production_order_id(value=value)

    @classmethod
    def validate_product_id(cls, value):
        return ProductionReportValid.validate_product_id(value=value)

    @classmethod
    def validate_uom_id(cls, value):
        return ProductionReportValid.validate_uom_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return ProductionReportValid.validate_warehouse_id(value=value)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        ProductionReportSub.create_sub_models(validated_data=validated_data, instance=instance)
        return instance


class ProductionReportGRSerializer(serializers.ModelSerializer):
    production_report_id = serializers.SerializerMethodField()
    production_report_data = serializers.SerializerMethodField()
    product_quantity_order_actual = serializers.SerializerMethodField()
    quantity_order = serializers.SerializerMethodField()
    gr_completed_quantity = serializers.SerializerMethodField()
    pr_products_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductionReport
        fields = (
            'id',
            'production_order_id',
            'production_report_id',
            'production_report_data',
            'title',
            'code',
            'product_id',
            'product_data',
            'quantity',
            'uom_id',
            'uom_data',
            'warehouse_data',
            'product_quantity_order_actual',
            'quantity_order',
            'gr_completed_quantity',
            'gr_remain_quantity',
            'pr_products_data',
        )

    @classmethod
    def get_production_report_id(cls, obj):
        return obj.id

    @classmethod
    def get_production_report_data(cls, obj):
        return {'id': str(obj.id), 'title': obj.title, 'code': obj.code}

    @classmethod
    def get_product_quantity_order_actual(cls, obj):
        return obj.quantity_finished

    @classmethod
    def get_quantity_order(cls, obj):
        return obj.quantity_finished

    @classmethod
    def get_gr_completed_quantity(cls, obj):
        return obj.quantity_finished - obj.gr_remain_quantity

    @classmethod
    def get_pr_products_data(cls, obj):
        return [] if obj else None
