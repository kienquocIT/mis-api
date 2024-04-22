from rest_framework import serializers
from apps.sales.inventory.models import GoodsReceipt


class GoodsDetailListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = GoodsReceipt
        fields = (
            'product_data',
        )

    @classmethod
    def get_product_data(cls, obj):
        return [{
            'goods_receipt': {
                'id': obj.id,
                'code': obj.code,
                'title': obj.title,
                'date_approved': obj.date_approved
            },
            'person_in_charge': {
                'id': obj.employee_inherit_id,
                'code': obj.employee_inherit.code,
                'full_name': obj.employee_inherit.get_full_name(2)
            } if obj.employee_inherit else {},
            'product': {
                'id': item.product_id,
                'code': item.product.code,
                'title': item.product.title
            } if item.product else {},
            'warehouse': {
                'id': item.goods_receipt_warehouse_gr_product.all().first().warehouse_id,
                'code': item.goods_receipt_warehouse_gr_product.all().first().warehouse.code,
                'title': item.goods_receipt_warehouse_gr_product.all().first().warehouse.title
            } if item.goods_receipt_warehouse_gr_product.all().first() else {},
            'quantity_import': item.quantity_import
        } for item in obj.goods_receipt_product_goods_receipt.all()]
