from rest_framework import serializers

from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer


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
            'group': {
                'id': obj.group_inherit_id,
                'title': obj.group_inherit.title,
            } if obj.group_inherit else {},
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


class ReportProductListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ReportProduct
        fields = (
            'id',
            'product',
            'date_approved',
            'revenue',
            'gross_profit',
            'net_income',
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product_id,
            'title': obj.product.title,
            'code': obj.product.code,
            'general_product_category': {
                'id': obj.product.general_product_category_id,
                'title': obj.product.general_product_category.title,
                'code': obj.product.general_product_category.code,
                'description': obj.product.general_product_category.description,
            } if obj.product.general_product_category else {}
        } if obj.product else {}


class ReportCustomerListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = ReportCustomer
        fields = (
            'id',
            'customer',
            'date_approved',
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
            'industry': {
                'id': obj.customer.industry_id,
                'title': obj.customer.industry.title,
                'code': obj.customer.industry.code,
                'description': obj.customer.industry.description,
            } if obj.customer.industry else {}
        } if obj.customer else {}
