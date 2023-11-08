from rest_framework import serializers

from apps.sales.report.models import ReportRevenue


class ReportRevenueListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = ReportRevenue
        fields = (
            'id',
            'sale_order',
            'date_approved',
            'revenue',
            'gross_profit',
            'net_income',
        )

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'title': obj.sale_order.title,
            'code': obj.sale_order.code,
            'customer': {
                'id': obj.sale_order.customer_id,
                'title': obj.sale_order.customer.name,
                'code': obj.sale_order.customer.code,
            } if obj.sale_order.customer else {},
            'employee_inherit': {
                'id': obj.sale_order.employee_inherit_id,
                'first_name': obj.sale_order.employee_inherit.first_name,
                'last_name': obj.sale_order.employee_inherit.last_name,
                'email': obj.sale_order.employee_inherit.email,
                'full_name': obj.sale_order.employee_inherit.get_full_name(2),
                'code': obj.sale_order.employee_inherit.code,
                'is_active': obj.sale_order.employee_inherit.is_active,
            } if obj.sale_order.employee_inherit else {},
        } if obj.sale_order else {}
