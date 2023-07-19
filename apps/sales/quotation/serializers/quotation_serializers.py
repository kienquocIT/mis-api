from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.quotation.models import Quotation, QuotationProduct, QuotationTerm, QuotationLogistic, \
    QuotationCost, QuotationExpense, QuotationIndicator
from apps.sales.quotation.serializers.quotation_sub import QuotationCommonCreate, QuotationCommonValidate
from apps.shared import SaleMsg


class QuotationProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
        max_length=550,
        allow_null=True
    )
    unit_of_measure = serializers.CharField(
        max_length=550,
        allow_null=True
    )
    tax = serializers.CharField(
        max_length=550,
        required=False
    )
    promotion = serializers.CharField(
        max_length=550,
        allow_null=True
    )
    shipping = serializers.CharField(
        max_length=550,
        allow_null=True
    )

    class Meta:
        model = QuotationProduct
        fields = (
            'product',
            'unit_of_measure',
            'tax',
            # product information
            'product_title',
            'product_code',
            'product_description',
            'product_uom_title',
            'product_uom_code',
            'product_quantity',
            'product_unit_price',
            'product_discount_value',
            'product_discount_amount',
            'product_tax_title',
            'product_tax_value',
            'product_tax_amount',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            'is_promotion',
            'promotion',
            'is_shipping',
            'shipping'
        )

    @classmethod
    def validate_product(cls, value):
        return QuotationCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return QuotationCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return QuotationCommonValidate().validate_tax(value=value)

    @classmethod
    def validate_promotion(cls, value):
        return QuotationCommonValidate().validate_promotion(value=value)

    @classmethod
    def validate_shipping(cls, value):
        return QuotationCommonValidate().validate_shipping(value=value)


class QuotationTermSerializer(serializers.ModelSerializer):
    price_list = serializers.ListField(
        child=serializers.CharField(
            max_length=550
        ),
        required=False
    )
    payment_term = serializers.CharField(
        max_length=550
    )

    class Meta:
        model = QuotationTerm
        fields = (
            'price_list',
            'payment_term'
        )

    @classmethod
    def validate_price_list(cls, value):
        return QuotationCommonValidate().validate_price_list(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return QuotationCommonValidate().validate_payment_term(value=value)


class QuotationLogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLogistic
        fields = (
            'shipping_address',
            'billing_address',
        )


class QuotationCostSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
        max_length=550,
        allow_null=True
    )
    unit_of_measure = serializers.CharField(
        max_length=550,
        allow_null=True
    )
    tax = serializers.CharField(
        max_length=550,
        required=False
    )
    shipping = serializers.CharField(
        max_length=550,
        allow_null=True
    )

    class Meta:
        model = QuotationCost
        fields = (
            'product',
            'unit_of_measure',
            'tax',
            # product information
            'product_title',
            'product_code',
            'product_uom_title',
            'product_uom_code',
            'product_quantity',
            'product_cost_price',
            'product_tax_title',
            'product_tax_value',
            'product_tax_amount',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            'is_shipping',
            'shipping',
        )

    @classmethod
    def validate_product(cls, value):
        return QuotationCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return QuotationCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return QuotationCommonValidate().validate_tax(value=value)

    @classmethod
    def validate_shipping(cls, value):
        return QuotationCommonValidate().validate_shipping(value=value)


class QuotationExpenseSerializer(serializers.ModelSerializer):
    expense = serializers.CharField(
        max_length=550
    )
    unit_of_measure = serializers.CharField(
        max_length=550
    )
    tax = serializers.CharField(
        max_length=550,
        required=False
    )

    class Meta:
        model = QuotationExpense
        fields = (
            'expense',
            'unit_of_measure',
            'tax',
            # expense information
            'expense_title',
            'expense_code',
            'expense_type_title',
            'expense_uom_title',
            'expense_uom_code',
            'expense_quantity',
            'expense_price',
            'expense_tax_title',
            'expense_tax_value',
            'expense_tax_amount',
            'expense_subtotal_price',
            'expense_subtotal_price_after_tax',
            'order',
        )

    @classmethod
    def validate_expense(cls, value):
        return QuotationCommonValidate().validate_expense(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return QuotationCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return QuotationCommonValidate().validate_tax(value=value)


class QuotationIndicatorSerializer(serializers.ModelSerializer):
    indicator = serializers.CharField(
        max_length=550
    )

    class Meta:
        model = QuotationIndicator
        fields = (
            'indicator',
            'indicator_value',
            'indicator_rate',
            'order',
        )

    @classmethod
    def validate_indicator(cls, value):
        return QuotationCommonValidate().validate_indicator(value=value)


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
        if obj.customer:
            return {
                'id': obj.customer_id,
                'title': obj.customer.name,
                'code': obj.customer.code,
            }
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.sale_person:
            return {
                'id': obj.sale_person_id,
                'full_name': obj.sale_person.get_full_name(2),
                'code': obj.sale_person.code,
            }
        return {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status:
            return "Open"
        return "Open"

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'title': obj.opportunity.title,
                'code': obj.opportunity.code,
            }
        return {}


class QuotationDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    payment_term = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

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
        )

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'title': obj.opportunity.title,
                'code': obj.opportunity.code,
                'customer': {
                    'id': obj.opportunity.customer_id,
                    'title': obj.opportunity.customer.title
                } if obj.opportunity.customer else {}
            }
        return {}

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return {
                'id': obj.customer_id,
                'title': obj.customer.name,
                'code': obj.customer.code,
                'payment_term_mapped': {
                    'id': obj.customer.payment_term_mapped_id,
                    'title': obj.customer.payment_term_mapped.title,
                    'code': obj.customer.payment_term_mapped.code,
                } if obj.customer.payment_term_mapped else {},
                'customer_price_list': obj.customer.price_list_mapped_id,
            }
        return {}

    @classmethod
    def get_contact(cls, obj):
        if obj.contact:
            return {
                'id': obj.contact_id,
                'title': obj.contact.fullname,
                'code': obj.contact.code,
            }
        return {}

    @classmethod
    def get_sale_person(cls, obj):
        if obj.sale_person:
            return {
                'id': obj.sale_person_id,
                'full_name': obj.sale_person.get_full_name(2),
                'code': obj.sale_person.code,
            }
        return {}

    @classmethod
    def get_payment_term(cls, obj):
        if obj.payment_term:
            return {
                'id': obj.payment_term_id,
                'title': obj.payment_term.title,
                'code': obj.payment_term.code,
            }
        return {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status:
            return "Open"
        return "Open"


# Quotation
class QuotationCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    opportunity = serializers.CharField(
        max_length=550,
        required=False,
        allow_null=True,
    )
    customer = serializers.CharField(
        max_length=550
    )
    contact = serializers.CharField(
        max_length=550
    )
    sale_person = serializers.CharField(
        max_length=550
    )
    payment_term = serializers.CharField(
        max_length=550
    )
    # quotation tabs
    quotation_products_data = QuotationProductSerializer(
        many=True,
        required=False
    )
    quotation_term_data = QuotationTermSerializer(required=False)
    quotation_logistic_data = QuotationLogisticSerializer(required=False)
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
            'opportunity',
            'customer',
            'contact',
            'sale_person',
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
    def validate_opportunity(cls, value):
        return QuotationCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return QuotationCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_sale_person(cls, value):
        return QuotationCommonValidate().validate_sale_person(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return QuotationCommonValidate().validate_payment_term(value=value)

    def validate(self, validate_data):
        if 'opportunity' in validate_data:
            if validate_data['opportunity'] is not None:
                if validate_data['opportunity'].quotation_opportunity.exists():
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_QUOTATION_USED})
                if validate_data['opportunity'].is_close_lost is True or validate_data['opportunity'].is_deal_close:
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    # @decorator_run_workflow
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
    opportunity = serializers.CharField(
        max_length=550,
        required=False,
        allow_null=True,
    )
    customer = serializers.CharField(
        max_length=550,
        required=False
    )
    contact = serializers.CharField(
        max_length=550,
        required=False
    )
    sale_person = serializers.CharField(
        max_length=550,
        required=False
    )
    payment_term = serializers.CharField(
        max_length=550,
        required=False
    )
    # quotation tabs
    quotation_products_data = QuotationProductSerializer(
        many=True,
        required=False
    )
    quotation_term_data = QuotationTermSerializer(required=False)
    quotation_logistic_data = QuotationLogisticSerializer(required=False)
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
            'opportunity',
            'customer',
            'contact',
            'sale_person',
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
            'quotation_costs_data',
            'quotation_expenses_data',
            'is_customer_confirm',
            # indicator tab
            'quotation_indicators_data',
        )

    @classmethod
    def validate_customer(cls, value):
        return QuotationCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity(cls, value):
        return QuotationCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return QuotationCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_sale_person(cls, value):
        return QuotationCommonValidate().validate_sale_person(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return QuotationCommonValidate().validate_payment_term(value=value)

    def validate(self, validate_data):
        if 'opportunity' in validate_data:
            if validate_data['opportunity'] is not None:
                if validate_data['opportunity'].quotation_opportunity.exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_QUOTATION_USED})
        return validate_data

    def update(self, instance, validated_data):
        # check if change opportunity then update field quotation in opportunity to None
        if instance.opportunity != validated_data.get('opportunity', None):
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

    class Meta:
        model = QuotationExpense
        fields = (
            'id',
            'expense_title',
            'expense_id',
            'tax',
            'plan_after_tax'
        )

    @classmethod
    def get_tax(cls, obj):
        if obj.tax:
            return {'id': obj.tax_id, 'code': obj.tax.code, 'title': obj.tax.title}
        return {}

    @classmethod
    def get_plan_after_tax(cls, obj):
        return obj.expense_subtotal_price + obj.expense_tax_amount
