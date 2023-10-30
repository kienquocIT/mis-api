from rest_framework import serializers

from apps.sales.saleorder.models import SaleOrder


class RevenueReportListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    gross_profit = serializers.SerializerMethodField()
    net_income = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'customer',
            'date_created',
            'revenue',
            'gross_profit',
            'net_income',
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
    def get_revenue(cls, obj):
        revenue = obj.sale_order_indicator_sale_order.filter(
            company_id=obj.company_id,
            quotation_indicator__title__contains="Revenue"
        ).first()
        if revenue:
            return revenue
        return 0

    @classmethod
    def get_gross_profit(cls, obj):
        return 1000000

    @classmethod
    def get_net_income(cls, obj):
        return 1000000
