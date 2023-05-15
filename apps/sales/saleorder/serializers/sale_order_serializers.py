from rest_framework import serializers

from apps.sales.saleorder.serializers.sale_order_sub import SaleOrderCommonCreate, SaleOrderCommonValidate
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderLogistic, SaleOrderCost, SaleOrderExpense, SaleOrder


class SaleOrderProductSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
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
        model = SaleOrderProduct
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
        return SaleOrderCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)


class SaleOrderLogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderLogistic
        fields = (
            'shipping_address',
            'billing_address',
        )


class SaleOrderCostSerializer(serializers.ModelSerializer):
    product = serializers.CharField(
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
        model = SaleOrderCost
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
        return SaleOrderCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)


class SaleOrderExpenseSerializer(serializers.ModelSerializer):
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
        model = SaleOrderExpense
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
        return SaleOrderCommonValidate().validate_expense(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)


# SALE ORDER BEGIN
class SaleOrderListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
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


class SaleOrderDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    payment_term = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'opportunity',
            'customer',
            'contact',
            'sale_person',
            'payment_term',
            'quotation',
            'system_status',
            # quotation tabs
            'sale_order_products_data',
            'sale_order_logistic_data',
            'sale_order_costs_data',
            'sale_order_expenses_data',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount_rate',
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
        )

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'title': obj.opportunity.title,
                'code': obj.opportunity.code,
            }
        return {}

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
    def get_quotation(cls, obj):
        if obj.quotation:
            return {
                'id': obj.quotation_id,
                'title': obj.quotation.title,
                'code': obj.quotation.code,
            }
        return {}

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status:
            return "Open"
        return "Open"


class SaleOrderCreateSerializer(serializers.ModelSerializer):
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
    payment_term = serializers.CharField(
        max_length=550
    )
    quotation = serializers.CharField(
        max_length=550
    )
    # sale order tabs
    sale_order_products_data = SaleOrderProductSerializer(
        many=True,
        required=False
    )
    sale_order_logistic_data = SaleOrderLogisticSerializer(required=False)
    sale_order_costs_data = SaleOrderCostSerializer(
        many=True,
        required=False
    )
    sale_order_expenses_data = SaleOrderExpenseSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = SaleOrder
        fields = (
            'title',
            'opportunity',
            'customer',
            'contact',
            'sale_person',
            'payment_term',
            'quotation',
            # total amount of products
            'total_product_pretax_amount',
            'total_product_discount_rate',
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
            # sale order tabs
            'sale_order_products_data',
            'sale_order_logistic_data',
            'sale_order_costs_data',
            'sale_order_expenses_data',
        )

    @classmethod
    def validate_customer(cls, value):
        return SaleOrderCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity(cls, value):
        return SaleOrderCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return SaleOrderCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_sale_person(cls, value):
        return SaleOrderCommonValidate().validate_sale_person(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return SaleOrderCommonValidate().validate_payment_term(value=value)

    @classmethod
    def validate_quotation(cls, value):
        return SaleOrderCommonValidate().validate_quotation(value=value)

    def create(self, validated_data):
        sale_order = SaleOrder.objects.create(**validated_data)
        SaleOrderCommonCreate().create_sale_order_sub_models(
            validated_data=validated_data,
            instance=sale_order
        )
        return sale_order


class SaleOrderUpdateSerializer(serializers.ModelSerializer):
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
    # sale order tabs
    sale_order_products_data = SaleOrderProductSerializer(
        many=True,
        required=False
    )
    sale_order_logistic_data = SaleOrderLogisticSerializer(required=False)
    sale_order_costs_data = SaleOrderCostSerializer(
        many=True,
        required=False
    )
    sale_order_expenses_data = SaleOrderExpenseSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = SaleOrder
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
            'sale_order_products_data',
            'sale_order_logistic_data',
            'sale_order_costs_data',
            'sale_order_expenses_data',
        )

    @classmethod
    def validate_customer(cls, value):
        return SaleOrderCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity(cls, value):
        return SaleOrderCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return SaleOrderCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_sale_person(cls, value):
        return SaleOrderCommonValidate().validate_sale_person(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return SaleOrderCommonValidate().validate_payment_term(value=value)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        SaleOrderCommonCreate().create_sale_order_sub_models(
            validated_data=validated_data,
            instance=instance,
            is_update=True
        )
        return instance
