from rest_framework import serializers

# from apps.sales.opportunity.models import OpportunityConfigStage
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer, ReportPipeline, ReportCashflow


# REPORT REVENUE
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
            'group_inherit_id'
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


# REPORT PRODUCT
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


# REPORT CUSTOMER
class ReportCustomerListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = ReportCustomer
        fields = (
            'id',
            'customer',
            'date_approved',
            'revenue',
            'gross_profit',
            'net_income',
            'employee_inherit'
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


# REPORT PIPELINE
class ReportPipelineListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = ReportPipeline
        fields = (
            'id',
            'opportunity',
            'employee_inherit',
            'group',
        )

    @classmethod
    def get_opportunity(cls, obj):
        stage = obj.opportunity.opportunity_stage_opportunity.select_related('stage').filter(is_current=True).first()
        stage_current = {}
        if stage:
            stage_current = {
                'id': stage.stage_id,
                'is_current': stage.is_current,
                'indicator': stage.stage.indicator,
                'win_rate': stage.stage.win_rate
            }
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'open_date': obj.opportunity.open_date,
            'close_date': obj.opportunity.close_date,
            'value': obj.opportunity.total_product_pretax_amount,
            'win_rate': obj.opportunity.win_rate,
            'forecast_value': (obj.opportunity.total_product_pretax_amount * obj.opportunity.win_rate) / 100,
            'gross_profit': (obj.opportunity.estimated_gross_profit_value * obj.opportunity.win_rate) / 100,
            'customer': {
                'id': obj.opportunity.customer_id,
                'title': obj.opportunity.customer.name,
                'code': obj.opportunity.customer.code,
            } if obj.opportunity.customer else {},
            'call': obj.opportunity.opportunity_calllog.count(),
            'email': obj.opportunity.opportunity_send_email.count(),
            'meeting': obj.opportunity.opportunity_meeting.count(),
            'document': obj.opportunity.opportunity_document.count(),
            'stage': stage_current
        }

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
            'group_id': obj.employee_inherit.group_id,
        } if obj.employee_inherit else {}

    @classmethod
    def get_group(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title
            } if obj.employee_inherit.group else {}
        return {}


# REPORT CASHFLOW
class ReportCashflowListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportCashflow
        fields = (
            'id',
            'cashflow_type',
            'due_date',
            # so
            'value_estimate_sale',
            'value_actual_sale',
            'value_variance_sale',
            # po
            'value_estimate_cost',
            'value_actual_cost',
            'value_variance_cost',
        )
