from rest_framework import serializers

from apps.sales.quotation.models.quotation import Quotation, QuotationProduct, QuotationTerm, QuotationLogistic, \
    QuotationCost, QuotationExpense, QuotationTermPrice, QuotationTermDiscount, QuotationLogisticShipping, \
    QuotationLogisticBilling


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
            'product_tax_title',
            'product_tax_value',
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
            'product',
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
            'expense_subtotal_price',
            'order',
        )


class QuotationCommon:

    @classmethod
    def validate_product_cost(cls, dict_data):
        product_id = None
        unit_of_measure_id = None
        tax_id = None
        if 'product' in dict_data:
            product_id = dict_data['product']
            del dict_data['product']
        if 'unit_of_measure' in dict_data:
            unit_of_measure_id = dict_data['unit_of_measure']
            del dict_data['unit_of_measure']
        if 'tax' in dict_data:
            tax_id = dict_data['tax']
            del dict_data['tax']
        return product_id, unit_of_measure_id, tax_id

    @classmethod
    def create_product(cls, validated_data, quotation):
        for quotation_product in validated_data['quotation_products_data']:
            product_id, unit_of_measure_id, tax_id = cls.validate_product_cost(dict_data=quotation_product)
            QuotationProduct.objects.create(
                quotation=quotation,
                product_id=product_id,
                unit_of_measure_id=unit_of_measure_id,
                tax_id=tax_id,
                **quotation_product
            )
        return True

    @classmethod
    def create_term(cls, validated_data, quotation):
        price_list = []
        discount_list = []
        payment_term = {}
        if 'price_list' in validated_data['quotation_term_data']:
            price_list = validated_data['quotation_term_data']['price_list']
            del validated_data['quotation_term_data']['price_list']
        if 'discount_list' in validated_data['quotation_term_data']:
            discount_list = validated_data['quotation_term_data']['discount_list']
            del validated_data['quotation_term_data']['discount_list']
        if 'payment_term' in validated_data['quotation_term_data']:
            payment_term = validated_data['quotation_term_data']['payment_term']
            del validated_data['quotation_term_data']['payment_term']
        quotation_term = QuotationTerm.objects.create(
            payment_term_id=payment_term.get('id', None),
            quotation=quotation
        )
        if price_list:
            QuotationTermPrice.objects.bulk_create([
                QuotationTermPrice(
                    price_id=price.get('id', None),
                    quotation_term=quotation_term
                )
                for price in price_list
            ])
        if discount_list:
            QuotationTermDiscount.objects.bulk_create([
                QuotationTermDiscount(
                    discount_id=discount.get('id', None),
                    quotation_term=quotation_term
                )
                for discount in discount_list
            ])
        return True

    @classmethod
    def create_logistic(cls, validated_data, quotation):
        shipping_address_list = []
        billing_address_list = []
        if 'shipping_address_list' in validated_data['quotation_logistic_data']:
            shipping_address_list = validated_data['quotation_logistic_data']['shipping_address_list']
            del validated_data['quotation_logistic_data']['shipping_address_list']
        if 'billing_address_list' in validated_data['quotation_logistic_data']:
            billing_address_list = validated_data['quotation_logistic_data']['billing_address_list']
            del validated_data['quotation_logistic_data']['billing_address_list']
        quotation_logistic = QuotationLogistic.objects.create(quotation=quotation)
        if shipping_address_list:
            QuotationLogisticShipping.objects.bulk_create([
                QuotationLogisticShipping(
                    shipping_address_id=shipping_address.get('id', None),
                    quotation_logistic=quotation_logistic
                )
                for shipping_address in shipping_address_list
            ])
        if billing_address_list:
            QuotationLogisticBilling.objects.bulk_create([
                QuotationLogisticBilling(
                    billing_address_id=billing_address.get('id', None),
                    quotation_logistic=quotation_logistic
                )
                for billing_address in billing_address_list
            ])
        return True

    @classmethod
    def create_cost(cls, validated_data, quotation):
        for quotation_cost in validated_data['quotation_costs_data']:
            product_id, unit_of_measure_id, tax_id = cls.validate_product_cost(dict_data=quotation_cost)
            QuotationCost.objects.create(
                quotation=quotation,
                product_id=product_id,
                unit_of_measure_id=unit_of_measure_id,
                tax_id=tax_id,
                **quotation_cost
            )
        return True

    @classmethod
    def create_expense(cls, validated_data, quotation):
        for quotation_expense in validated_data['quotation_expenses_data']:
            expense_id = None
            unit_of_measure_id = None
            tax_id = None
            if 'expense' in quotation_expense:
                expense_id = quotation_expense['expense']
                del quotation_expense['expense']
            if 'unit_of_measure' in quotation_expense:
                unit_of_measure_id = quotation_expense['unit_of_measure']
                del quotation_expense['unit_of_measure']
            if 'tax' in quotation_expense:
                tax_id = quotation_expense['tax']
                del quotation_expense['tax']
            QuotationExpense.objects.create(
                quotation=quotation,
                expense_id=expense_id,
                unit_of_measure_id=unit_of_measure_id,
                tax_id=tax_id,
                **quotation_expense
            )
        return True


# Quotation
class QuotationCreateSerializer(serializers.ModelSerializer):
    opportunity = serializers.CharField(
        max_length=550
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
            'total_pretax_revenue',
            'total_tax',
            'total',
            'is_customer_confirm',
            # quotation tabs
            'quotation_products_data',
            'quotation_term_data',
            'quotation_logistic_data',
            'quotation_costs_data',
            'quotation_expenses_data'
        )

    def create(self, validated_data):
        quotation = Quotation.objects.create(**validated_data)
        if 'quotation_products_data' in validated_data:
            QuotationCommon().create_product(
                validated_data=validated_data,
                quotation=quotation
            )
        if 'quotation_term_data' in validated_data:
            QuotationCommon().create_term(
                validated_data=validated_data,
                quotation=quotation
            )
        if 'quotation_logistic_data' in validated_data:
            QuotationCommon().create_logistic(
                validated_data=validated_data,
                quotation=quotation
            )
        if 'quotation_costs_data' in validated_data:
            QuotationCommon().create_cost(
                validated_data=validated_data,
                quotation=quotation
            )
        if 'quotation_expenses_data' in validated_data:
            QuotationCommon().create_expense(
                validated_data=validated_data,
                quotation=quotation
            )
        return quotation
