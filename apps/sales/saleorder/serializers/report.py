from rest_framework import serializers

from apps.sales.saleorder.models import SaleOrder


class RevenueReportListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    indicator = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'customer',
            'date_created',
            'indicator',
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}

    @classmethod
    def get_indicator(cls, obj):
        return [
            {
                'id': so_indicator.id,
                'code': so_indicator.code,
                'indicator_value': so_indicator.indicator_value,
            } for so_indicator in obj.sale_order_indicator_sale_order.all()
        ]
