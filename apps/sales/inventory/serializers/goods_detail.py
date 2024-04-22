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
                'title': item.product.title,
                'type': item.product.general_traceability_method
            } if item.product else {},
            'warehouse': {
                'id': item.goods_receipt_warehouse_gr_product.first().warehouse_id,
                'code': item.goods_receipt_warehouse_gr_product.first().warehouse.code,
                'title': item.goods_receipt_warehouse_gr_product.first().warehouse.title
            } if item.goods_receipt_warehouse_gr_product.first() else {},
            'serial_list': [{
                'id': serial.id,
                'vendor_serial_number': serial.vendor_serial_number,
                'serial_number': serial.serial_number,
                'expire_date': serial.expire_date,
                'manufacture_date': serial.manufacture_date,
                'warranty_start': serial.warranty_start,
                'warranty_end': serial.warranty_end
            } for serial in item.goods_receipt_warehouse_gr_product.first().goods_receipt_serial_gr_warehouse.all(
                ).order_by('serial_number')],
            'quantity_import': item.quantity_import
        } for item in obj.goods_receipt_product_goods_receipt.all()]
