from rest_framework import serializers
from apps.sales.report.models import ReportInventory


class ReportInventoryListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ReportInventory
        fields = (
            'id',
            'product',
            'order',
            'stock_quantity',
            'stock_unit_price',
            'stock_subtotal_price'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'description': obj.product.description,
        } if obj.product else {}
