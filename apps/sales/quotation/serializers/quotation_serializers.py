from rest_framework import serializers

from apps.sale.saledata.models.accounts import Account
from apps.sales.quotation.models import Quotation, QuotationProduct, QuotationTerm, QuotationLogistic, \
    QuotationCost, QuotationExpense
from apps.sales.quotation.serializers.quotation_sub import QuotationCommon
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


class QuotationLogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLogistic
        fields = (
            'shipping_address',
            'shipping_address',
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


# QUOTATION BEGIN
class QuotationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code'
        )


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
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': AccountsMsg.ACCOUNT_NOT_EXIST})

    def create(self, validated_data):
        quotation = Quotation.objects.create(**validated_data)
        QuotationCommon().create_quotation_sub_models(
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
        QuotationCommon().create_quotation_sub_models(
            validated_data=validated_data,
            instance=instance
        )
        return instance
