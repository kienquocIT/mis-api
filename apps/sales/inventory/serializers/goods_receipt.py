from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.inventory.models import GoodsReceipt, GoodsReceiptProduct
from apps.shared import SYSTEM_STATUS


class GoodsReceiptProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptProduct
        fields = (
            'purchase_order_product',
            'purchase_request_products_data',
            'product',
            'uom',
            'tax',
            'quantity_import',
            'product_title',
            'product_code',
            'product_description',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
        )


# GOODS RECEIPT BEGIN
class GoodsReceiptListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'supplier',
            'system_status',
        )

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class GoodsReceiptDetailSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'id',
            'title',
            'code',
            'supplier',
            # system
            'system_status',
            'workflow_runtime_id',
        )

    @classmethod
    def get_supplier(cls, obj):
        return {
            'id': obj.supplier_id,
            'name': obj.supplier.name,
            'code': obj.supplier.code,
        } if obj.supplier else {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class GoodsReceiptCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    supplier = serializers.UUIDField(required=False)
    goods_receipt_product = GoodsReceiptProductSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'title',
            'purchase_order',
            'supplier',
            'purchase_requests',
            'remarks',
            # line detail
            'goods_receipt_product',
            # system
            'system_status',
        )

    @decorator_run_workflow
    def create(self, validated_data):
        goods_receipt = GoodsReceipt.objects.create(**validated_data)
        return goods_receipt


class GoodsReceiptUpdateSerializer(serializers.ModelSerializer):
    supplier = serializers.UUIDField(required=False)

    class Meta:
        model = GoodsReceipt
        fields = (
            'title',
            'supplier',
            # system
            'system_status',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
