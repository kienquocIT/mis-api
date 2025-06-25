from django.utils import timezone
from rest_framework import serializers

# from apps.sales.opportunity.models import OpportunityConfigStage
from apps.sales.report.models import ReportRevenue, ReportProduct, ReportCustomer, ReportPipeline, ReportCashflow, \
    ReportLease


class ReportCommonGet:

    @classmethod
    def get_employee(cls, employee_obj):
        return {
            'id': getattr(employee_obj, 'id', None),
            'first_name': employee_obj.first_name,
            'last_name': employee_obj.last_name,
            'email': employee_obj.email,
            'full_name': employee_obj.get_full_name(2),
            'code': employee_obj.code,
            'is_active': employee_obj.is_active,
            'group_id': employee_obj.group_id,
            'is_delete': employee_obj.is_delete,
        } if employee_obj else {}

    @classmethod
    def get_group(cls, group_obj):
        return {
            'id': getattr(group_obj, 'id', None),
            'title': group_obj.title,
            'code': group_obj.code,
            'is_active': group_obj.is_active,
            'is_delete': group_obj.is_delete,
        } if group_obj else {}


# REPORT REVENUE
class ReportRevenueListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    lease_order = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = ReportRevenue
        fields = (
            'id',
            'sale_order',
            'lease_order',
            'quotation',
            'opportunity',
            'customer',
            'date_approved',
            'revenue',
            'gross_profit',
            'net_income',
            'employee_inherit',
            'group_inherit_id',
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
        } if obj.sale_order else {}

    @classmethod
    def get_lease_order(cls, obj):
        return {
            'id': obj.lease_order_id,
            'title': obj.lease_order.title,
            'code': obj.lease_order.code,
            'customer': {
                'id': obj.lease_order.customer_id,
                'title': obj.lease_order.customer.name,
                'code': obj.lease_order.customer.code,
            } if obj.lease_order.customer else {},
        } if obj.lease_order else {}

    @classmethod
    def get_quotation(cls, obj):
        return {
            'id': obj.quotation_id,
            'title': obj.quotation.title,
            'code': obj.quotation.code,
            'customer': {
                'id': obj.quotation.customer_id,
                'title': obj.quotation.customer.name,
                'code': obj.quotation.customer.code,
            } if obj.quotation.customer else {},
        } if obj.quotation else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return ReportCommonGet.get_employee(employee_obj=obj.employee_inherit)


# REPORT PRODUCT
class ReportProductListSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = ReportProduct
        fields = (
            'id',
            'sale_order',
            'product',
            'quantity',
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
            } if obj.sale_order.customer else {}
        } if obj.sale_order else {}

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
            } if obj.product.general_product_category else {},
            'uom': {
                'id': obj.product.sale_default_uom_id,
                'title': obj.product.sale_default_uom.title,
                'code': obj.product.sale_default_uom.code,
            } if obj.product.sale_default_uom else {},
        } if obj.product else {}


class ReportProductListSerializerForDashBoard(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ReportProduct
        fields = (
            'id',
            'product',
            'quantity',
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
            } if obj.product.general_product_category else {},
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
        return ReportCommonGet.get_employee(employee_obj=obj.employee_inherit)


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
        stage_current = {}
        for opp_stage in obj.opportunity.opportunity_stage_opportunity.all():
            if opp_stage.is_current is True:
                stage_current = {
                    'id': opp_stage.stage_id,
                    'is_current': True,
                    'indicator': opp_stage.stage.indicator if opp_stage.stage else '',
                    'win_rate': opp_stage.stage.win_rate if opp_stage.stage else 0,
                }
                break
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
        return ReportCommonGet.get_employee(employee_obj=obj.employee_inherit)

    @classmethod
    def get_group(cls, obj):
        return ReportCommonGet.get_group(group_obj=obj.employee_inherit.group) if obj.employee_inherit else {}


# REPORT CASHFLOW
class ReportCashflowListSerializer(serializers.ModelSerializer):
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = ReportCashflow
        fields = (
            'id',
            'cashflow_type',
            'due_date',
            'system_status',
            # so
            'value_estimate_sale',
            'value_actual_sale',
            'value_variance_sale',
            # po
            'value_estimate_cost',
            'value_actual_cost',
            'value_variance_cost',
        )

    @classmethod
    def get_system_status(cls, obj):
        if obj.sale_order:
            return obj.sale_order.system_status
        if obj.purchase_order:
            return obj.purchase_order.system_status
        return None


# REPORT GENERAL
class ReportGeneralListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    group_inherit = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()

    class Meta:
        model = ReportRevenue
        fields = (
            'id',
            'employee_inherit',
            'group_inherit',
            'revenue',
            'gross_profit',
            'plan',
        )

    @classmethod
    def get_employee_inherit(cls, obj):
        return ReportCommonGet.get_employee(employee_obj=obj.employee_inherit)

    @classmethod
    def get_group_inherit(cls, obj):
        return ReportCommonGet.get_group(group_obj=obj.employee_inherit.group) if obj.employee_inherit else {}

    @classmethod
    def get_plan(cls, obj):
        result = {}
        if obj.employee_inherit:
            for employee_plan in obj.employee_inherit.rp_group_employee_employee.all():
                if employee_plan.revenue_plan_mapped:
                    if employee_plan.revenue_plan_mapped.period_mapped:
                        year = employee_plan.revenue_plan_mapped.period_mapped.fiscal_year
                        if year not in result:
                            result.update({
                                str(year): {
                                    'revenue_year': employee_plan.emp_year_target,
                                    'revenue_quarter': employee_plan.emp_quarter_target,
                                    'revenue_month': employee_plan.emp_month_target,
                                    'profit_year': employee_plan.emp_year_profit_target,
                                    'profit_quarter': employee_plan.emp_quarter_profit_target,
                                    'profit_month': employee_plan.emp_month_profit_target,
                                },
                                'group_id': obj.employee_inherit.group_id,
                            })
        return result


# REPORT REVENUE
class ReportLeaseListSerializer(serializers.ModelSerializer):
    lease_order = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    lease_status = serializers.SerializerMethodField()

    class Meta:
        model = ReportLease
        fields = (
            'id',
            'lease_order',
            'opportunity',
            'customer',
            'lease_from',
            'lease_to',
            'date_approved',
            'revenue',
            'gross_profit',
            'net_income',
            'employee_inherit',
            'lease_status',
        )

    @classmethod
    def get_lease_order(cls, obj):
        return {
            'id': obj.lease_order_id,
            'title': obj.lease_order.title,
            'code': obj.lease_order.code,
            'customer': {
                'id': obj.lease_order.customer_id,
                'title': obj.lease_order.customer.name,
                'code': obj.lease_order.customer.code,
            } if obj.lease_order.customer else {},
        } if obj.lease_order else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return ReportCommonGet.get_employee(employee_obj=obj.employee_inherit)

    @classmethod
    def get_lease_status(cls, obj):
        status = 1
        if obj.lease_from and obj.lease_to:
            current = timezone.now()
            if current.date() < obj.lease_from:
                status = 1  # Prepare for lease
            if obj.lease_from <= current.date() <= obj.lease_to:
                status = 2  # Currently for lease
            if current.date() > obj.lease_to:
                status = 3  # Lease expires
        return status
