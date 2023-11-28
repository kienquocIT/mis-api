from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation, QuotationExpense
from apps.sales.quotation.serializers.quotation_sub import QuotationCommonCreate, QuotationCommonValidate, \
    QuotationProductsListSerializer, QuotationCostsListSerializer, QuotationProductSerializer, \
    QuotationTermSerializer, QuotationLogisticSerializer, QuotationCostSerializer, QuotationExpenseSerializer, \
    QuotationIndicatorSerializer
from apps.shared import SYSTEM_STATUS, SaleMsg, BaseMsg


# QUOTATION BEGIN
class QuotationListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'sale_person',
            'date_created',
            'total_product',
            'system_status',
            'opportunity'
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
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
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}


class QuotationDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    payment_term = serializers.SerializerMethodField()
    quotation_products_data = serializers.SerializerMethodField()
    quotation_costs_data = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code',
            'opportunity',
            'customer',
            'contact',
            'sale_person',
            'payment_term',
            'system_status',
            # quotation tabs
            'quotation_products_data',
            'quotation_term_data',
            'quotation_logistic_data',
            'customer_shipping_id',
            'customer_billing_id',
            'quotation_costs_data',
            'quotation_expenses_data',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount_rate',
            'total_product_discount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # total amount of costs
            'total_cost_pretax_amount',
            'total_cost_tax',
            'total_cost',
            # total amount of expenses
            'total_expense_pretax_amount',
            'total_expense_tax',
            'total_expense',
            'is_customer_confirm',
            'date_created',
            # indicator tab
            'quotation_indicators_data',
            # system
            'workflow_runtime_id',
            'is_active',
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'is_close_lost': obj.opportunity.is_close_lost,
            'is_deal_close': obj.opportunity.is_deal_close,
            'sale_order_id': obj.opportunity.sale_order_id,
            'customer': {
                'id': obj.opportunity.customer_id,
                'title': obj.opportunity.customer.title
            } if obj.opportunity.customer else {}
        } if obj.opportunity else {}

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
            'payment_term_mapped': {
                'id': obj.customer.payment_term_customer_mapped_id,
                'title': obj.customer.payment_term_customer_mapped.title,
                'code': obj.customer.payment_term_customer_mapped.code,
            } if obj.customer.payment_term_customer_mapped else {},
            'customer_price_list': obj.customer.price_list_mapped_id,
        } if obj.customer else {}

    @classmethod
    def get_contact(cls, obj):
        return {
            'id': obj.contact_id,
            'title': obj.contact.fullname,
            'code': obj.contact.code,
        } if obj.contact else {}

    @classmethod
    def get_sale_person(cls, obj):
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
    def get_payment_term(cls, obj):
        return {
            'id': obj.payment_term_id,
            'title': obj.payment_term.title,
            'code': obj.payment_term.code,
        } if obj.payment_term else {}

    @classmethod
    def get_quotation_products_data(cls, obj):
        return QuotationProductsListSerializer(
            obj.quotation_product_quotation.all(),
            many=True
        ).data

    @classmethod
    def get_quotation_costs_data(cls, obj):
        return QuotationCostsListSerializer(
            obj.quotation_cost_quotation.all(),
            many=True
        ).data


class QuotationCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer = serializers.UUIDField()
    contact = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    payment_term = serializers.UUIDField()
    # quotation tabs
    quotation_products_data = QuotationProductSerializer(
        many=True,
        required=False
    )
    quotation_term_data = QuotationTermSerializer(required=False)
    quotation_logistic_data = QuotationLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
    quotation_costs_data = QuotationCostSerializer(
        many=True,
        required=False
    )
    quotation_expenses_data = QuotationExpenseSerializer(
        many=True,
        required=False
    )
    # indicator tab
    quotation_indicators_data = QuotationIndicatorSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Quotation
        fields = (
            'title',
            'opportunity_id',
            'customer',
            'contact',
            'employee_inherit_id',
            'payment_term',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount_rate',
            'total_product_discount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # total amount of costs
            'total_cost_pretax_amount',
            'total_cost_tax',
            'total_cost',
            # total amount of expenses
            'total_expense_pretax_amount',
            'total_expense_tax',
            'total_expense',
            # quotation tabs
            'quotation_products_data',
            'quotation_term_data',
            'quotation_logistic_data',
            'customer_shipping',
            'customer_billing',
            'quotation_costs_data',
            'quotation_expenses_data',
            'is_customer_confirm',
            # indicator tab
            'quotation_indicators_data',
            # system
            'system_status',
        )

    @classmethod
    def validate_customer(cls, value):
        return QuotationCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return QuotationCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return QuotationCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return QuotationCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return QuotationCommonValidate().validate_payment_term(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return QuotationCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return QuotationCommonValidate().validate_customer_billing(value=value)

    def validate(self, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=validate_data['opportunity_id']
                ).first()
                if opportunity:
                    if opportunity.quotation_opportunity.exists():
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_QUOTATION_USED})
                    if opportunity.is_close_lost is True or opportunity.is_deal_close:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        quotation = Quotation.objects.create(**validated_data)
        QuotationCommonCreate().create_quotation_sub_models(
            validated_data=validated_data,
            instance=quotation
        )
        # update field quotation for opportunity
        if quotation.opportunity:
            quotation.opportunity.quotation = quotation
            quotation.opportunity.save(**{
                'update_fields': ['quotation'],
                'quotation_confirm': quotation.is_customer_confirm,
            })
        return quotation


class QuotationUpdateSerializer(serializers.ModelSerializer):
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    contact = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    employee_inherit_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    payment_term = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    # quotation tabs
    quotation_products_data = QuotationProductSerializer(
        many=True,
        required=False
    )
    quotation_term_data = QuotationTermSerializer(required=False)
    quotation_logistic_data = QuotationLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
    quotation_costs_data = QuotationCostSerializer(
        many=True,
        required=False
    )
    quotation_expenses_data = QuotationExpenseSerializer(
        many=True,
        required=False
    )
    # indicator tab
    quotation_indicators_data = QuotationIndicatorSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Quotation
        fields = (
            'title',
            'opportunity_id',
            'customer',
            'contact',
            'employee_inherit_id',
            'payment_term',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount_rate',
            'total_product_discount',
            'total_product_tax',
            'total_product',
            'total_product_revenue_before_tax',
            # total amount of costs
            'total_cost_pretax_amount',
            'total_cost_tax',
            'total_cost',
            # total amount of expenses
            'total_expense_pretax_amount',
            'total_expense_tax',
            'total_expense',
            # quotation tabs
            'quotation_products_data',
            'quotation_term_data',
            'quotation_logistic_data',
            'customer_shipping',
            'customer_billing',
            'quotation_costs_data',
            'quotation_expenses_data',
            'is_customer_confirm',
            # indicator tab
            'quotation_indicators_data',
            # status
            'system_status',
        )

    @classmethod
    def validate_customer(cls, value):
        return QuotationCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return QuotationCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return QuotationCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return QuotationCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return QuotationCommonValidate().validate_payment_term(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return QuotationCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return QuotationCommonValidate().validate_customer_billing(value=value)

    def validate_system_status(self, attrs):
        if attrs in [0, 1]:  # draft or created
            if self.instance.system_status <= attrs:
                return attrs
        raise serializers.ValidationError({
            'system_status': BaseMsg.SYSTEM_STATUS_INCORRECT,
        })

    def validate(self, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=validate_data['opportunity_id']
                ).first()
                if opportunity:
                    if opportunity.quotation_opportunity.exclude(id=self.instance.id).exists():
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_QUOTATION_USED})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        # check if change opportunity then update field quotation in opportunity to None
        if instance.opportunity_id != validated_data.get('opportunity_id', None):
            instance.opportunity.quotation = None
            instance.opportunity.save(update_fields=['quotation'])
        # update quotation
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        QuotationCommonCreate().create_quotation_sub_models(
            validated_data=validated_data,
            instance=instance,
            is_update=True
        )
        # update field quotation for opportunity
        if instance.opportunity:
            instance.opportunity.quotation = instance
            instance.opportunity.save(**{
                'update_fields': ['quotation'],
                'quotation_confirm': instance.is_customer_confirm,
            })
        return instance


class QuotationExpenseListSerializer(serializers.ModelSerializer):
    tax = serializers.SerializerMethodField()
    plan_after_tax = serializers.SerializerMethodField()
    expense_item = serializers.SerializerMethodField()

    class Meta:
        model = QuotationExpense
        fields = (
            'id',
            'expense_title',
            'expense_item',
            'tax',
            'plan_after_tax',
        )

    @classmethod
    def get_tax(cls, obj):
        if obj.tax:
            return {'id': obj.tax_id, 'code': obj.tax.code, 'title': obj.tax.title}
        return {}

    @classmethod
    def get_plan_after_tax(cls, obj):
        return obj.expense_subtotal_price + obj.expense_tax_amount

    @classmethod
    def get_expense_item(cls, obj):
        if obj.expense_item:
            return {'id': obj.expense_item_id, 'code': obj.expense_item.code, 'title': obj.expense_item.title}
        return {}
