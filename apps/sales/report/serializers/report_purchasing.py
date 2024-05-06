from rest_framework import serializers
from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderRequest


class PurchaseOrderListReportSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'title',
            'code',
            'supplier',
            'delivered_date',
            'employee_inherit',
            'sale_order',
            'product_data',
            'receipt_status',
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
    def get_sale_order(cls, obj):
        all_sale_order = []
        for pr in PurchaseOrderRequest.objects.filter(purchase_order=obj):
            all_sale_order.append(pr.purchase_request.sale_order_id)
        return all_sale_order

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'fullname': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}

    @classmethod
    def get_product_data(cls, obj):
        product_data = []
        for item in obj.purchase_order_product_order.all():
            product_data.append({
                'product': {
                    'id': item.product_id,
                    'code': item.product.code,
                    'title': item.product.title,
                    'product_type': [prd_type.id for prd_type in item.product.general_product_types_mapped.all()],
                    'product_category': item.product.general_product_category_id
                } if item.product else {},
                'uom': {
                    'id': item.uom_order_actual_id,
                    'code': item.uom_order_actual.code,
                    'title': item.uom_order_actual.title
                } if item.uom_order_actual else {},
                'order_quantity': item.product_quantity_order_actual,
                'received_quantity': item.gr_completed_quantity,
                'remaining_quantity': item.gr_remain_quantity,
                'order_value': item.product_quantity_order_actual * item.product_unit_price,
                'received_value': item.gr_completed_quantity * item.product_unit_price,
                'remaining_value': item.gr_remain_quantity * item.product_unit_price,
            })
        return product_data
