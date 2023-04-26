from rest_framework import serializers

from apps.sale.saledata.models.accounts import Account
from apps.sales.quotation.models import Quotation, QuotationProduct, QuotationTerm, QuotationLogistic, \
    QuotationCost, QuotationExpense
from apps.sales.quotation.serializers.quotation_sub import QuotationCommonCreate, QuotationCommonValidate
from apps.shared import AccountsMsg


class QuotationProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
        max_length=550
    )
    unit_of_measure = serializers.CharField(
        max_length=550
    )
    tax = serializers.CharField(
        max_length=550
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
            'order',
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


class QuotationTermSerializer(serializers.ModelSerializer):
    price_list = serializers.ListField(
        child=serializers.CharField(
            max_length=550
        ),
        required=False
    )
    discount_list = serializers.ListField(
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
            'discount_list',
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
        max_length=550
    )
    unit_of_measure = serializers.CharField(
        max_length=550
    )
    tax = serializers.CharField(
        max_length=550
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
            'order',
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


class QuotationExpenseSerializer(serializers.ModelSerializer):
    expense = serializers.CharField(
        max_length=550
    )
    unit_of_measure = serializers.CharField(
        max_length=550
    )
    tax = serializers.CharField(
        max_length=550
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
            'expense_uom_title',
            'expense_uom_code',
            'expense_quantity',
            'expense_price',
            'expense_tax_title',
            'expense_tax_value',
            'expense_tax_amount',
            'expense_subtotal_price',
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


# QUOTATION BEGIN
class QuotationListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

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
            'system_status'
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


class QuotationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code'
        )


# Quotation
class QuotationCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    opportunity = serializers.CharField(
        max_length=550,
        required=False
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

    class Meta:
        model = Quotation
        fields = (
            'title',
            'opportunity',
            'customer',
            'contact',
            'sale_person',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount',
            'total_product_tax',
            'total_product',
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

    def create(self, validated_data):
        quotation = Quotation.objects.create(**validated_data)
        QuotationCommonCreate().create_quotation_sub_models(
            validated_data=validated_data,
            instance=quotation
        )
        return quotation


class QuotationUpdateSerializer(serializers.ModelSerializer):
    opportunity = serializers.CharField(
        max_length=550,
        required=False
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

    class Meta:
        model = Quotation
        fields = (
            'title',
            'opportunity',
            'customer',
            'contact',
            'sale_person',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount',
            'total_product_tax',
            'total_product',
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
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': AccountsMsg.ACCOUNT_NOT_EXIST})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        QuotationCommonCreate().create_quotation_sub_models(
            validated_data=validated_data,
            instance=instance
        )
        return instance
