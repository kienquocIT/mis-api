from rest_framework import serializers

from apps.sales.quotation.serializers import QuotationCommonValidate
# from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.saleorder.serializers.sale_order_sub import SaleOrderCommonCreate, SaleOrderCommonValidate
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderLogistic, SaleOrderCost, SaleOrderExpense, \
    SaleOrder, SaleOrderIndicator
from apps.shared import SaleMsg, SYSTEM_STATUS


class SaleOrderProductSerializer(serializers.ModelSerializer):
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
            'product_subtotal_price_after_tax',
            'order',
            'is_promotion',
            'promotion',
            'is_shipping',
            'shipping'
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

    @classmethod
    def validate_promotion(cls, value):
        return SaleOrderCommonValidate().validate_promotion(value=value)

    @classmethod
    def validate_shipping(cls, value):
        return SaleOrderCommonValidate().validate_shipping(value=value)


class SaleOrderLogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderLogistic
        fields = (
            'shipping_address',
            'billing_address',
        )


class SaleOrderCostSerializer(serializers.ModelSerializer):
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
            'product_subtotal_price_after_tax',
            'order',
            'is_shipping',
            'shipping',
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

    @classmethod
    def validate_shipping(cls, value):
        return SaleOrderCommonValidate().validate_shipping(value=value)


class SaleOrderExpenseSerializer(serializers.ModelSerializer):
    expense = serializers.CharField(
        max_length=550,
        allow_null=True,
    )
    product = serializers.CharField(
        max_length=550,
        allow_null=True,
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
            'product',
            'unit_of_measure',
            'tax',
            # expense information
            'expense_title',
            'expense_code',
            'product_title',
            'product_code',
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
            'is_product',
        )

    @classmethod
    def validate_expense(cls, value):
        return SaleOrderCommonValidate().validate_expense(value=value)

    @classmethod
    def validate_product(cls, value):
        return QuotationCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)


class SaleOrderIndicatorSerializer(serializers.ModelSerializer):
    # indicator = serializers.CharField(
    #     max_length=550
    # )
    quotation_indicator = serializers.CharField(
        max_length=550
    )

    class Meta:
        model = SaleOrderIndicator
        fields = (
            # 'indicator',
            'quotation_indicator',
            'indicator_value',
            'indicator_rate',
            'quotation_indicator_value',
            'quotation_indicator_rate',
            'difference_indicator_value',
            'order',
        )

    # @classmethod
    # def validate_indicator(cls, value):
    #     return SaleOrderCommonValidate().validate_indicator(value=value)

    @classmethod
    def validate_quotation_indicator(cls, value):
        return QuotationCommonValidate().validate_indicator(value=value)


# SALE ORDER BEGIN
class SaleOrderListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()

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
            'system_status',
            'opportunity',
            'quotation',
            'delivery_call',
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
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'title': obj.opportunity.title,
                'code': obj.opportunity.code,
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
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


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
            # sale order tabs
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
            'total_product_revenue_before_tax',
            # total amount of costs
            'total_cost_pretax_amount',
            'total_cost_tax',
            'total_cost',
            # total amount of expenses
            'total_expense_pretax_amount',
            'total_expense_tax',
            'total_expense',
            'date_created',
            'delivery_call',
            # indicator tab
            'sale_order_indicators_data',
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
                } if obj.customer.payment_term_mapped else {}
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
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class SaleOrderCreateSerializer(serializers.ModelSerializer):
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
    quotation = serializers.CharField(
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
    # indicator tab
    sale_order_indicators_data = SaleOrderIndicatorSerializer(
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
            'total_product_revenue_before_tax',
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
            # indicator tab
            'sale_order_indicators_data',
            # system
            'system_status',
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

    def validate(self, validate_data):
        if 'opportunity' in validate_data:
            if validate_data['opportunity'] is not None:
                if validate_data['opportunity'].sale_order_opportunity.exists():
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_SALE_ORDER_USED})
                if validate_data['opportunity'].is_close_lost is True or validate_data['opportunity'].is_deal_close:
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    # @decorator_run_workflow
    def create(self, validated_data):
        sale_order = SaleOrder.objects.create(**validated_data)
        SaleOrderCommonCreate().create_sale_order_sub_models(
            validated_data=validated_data,
            instance=sale_order
        )
        # update field sale_order for opportunity
        if sale_order.opportunity:
            sale_order.opportunity.sale_order = sale_order
            sale_order.opportunity.save(
                **{
                    'update_fields': ['sale_order'],
                    'sale_order_status': sale_order.system_status,
                }
            )
        return sale_order


class SaleOrderUpdateSerializer(serializers.ModelSerializer):
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
    quotation = serializers.CharField(
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
    # indicator tab
    sale_order_indicators_data = SaleOrderIndicatorSerializer(
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
            'total_product_revenue_before_tax',
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
            # indicator tab
            'sale_order_indicators_data',
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

    def validate(self, validate_data):
        if 'opportunity' in validate_data:
            if validate_data['opportunity'] is not None:
                if validate_data['opportunity'].sale_order_opportunity.exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_SALE_ORDER_USED})
        return validate_data

    def update(self, instance, validated_data):
        # check if change opportunity then update field sale_order in opportunity to None
        if instance.opportunity != validated_data.get('opportunity', None):
            instance.opportunity.sale_order = None
            instance.opportunity.save(update_fields=['sale_order'])
        # update sale order
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        SaleOrderCommonCreate().create_sale_order_sub_models(
            validated_data=validated_data,
            instance=instance,
            is_update=True
        )
        # update field sale_order for opportunity
        if instance.opportunity:
            instance.opportunity.sale_order = instance
            instance.opportunity.save(
                **{
                    'update_fields': ['sale_order'],
                    'sale_order_status': instance.system_status,
                }
            )
        return instance


class SaleOrderExpenseListSerializer(serializers.ModelSerializer):
    tax = serializers.SerializerMethodField()
    plan_after_tax = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrderExpense
        fields = (
            'id',
            'expense_title',
            'expense_id',
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


class SaleOrderListSerializerForCashOutFlow(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()

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
            'system_status',
            'opportunity',
            'quotation',
            'delivery_call',
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
    def get_opportunity(cls, obj):
        if obj.opportunity:
            is_close = False
            if obj.opportunity.is_close_lost or obj.opportunity.is_deal_close:
                is_close = True
            return {
                'id': obj.opportunity_id,
                'title': obj.opportunity.title,
                'code': obj.opportunity.code,
                'opportunity_sale_team_datas': obj.opportunity.opportunity_sale_team_datas,
                'is_close': is_close
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


class SaleOrderProductListSerializer(serializers.ModelSerializer):
    product_data = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'product_data',
        )

    @classmethod
    def get_product_data(cls, obj):
        so_product = SaleOrderProduct.objects.select_related('product').filter(sale_order=obj, product__isnull=False)
        return [
            {
                'id': item.id,
                'product_quantity': item.product_quantity,
                'remain_for_purchase_request': item.remain_for_purchase_request,
                'product': {
                    'id': item.product_id,
                    'title': item.product.title,
                    'code': item.product.code,
                    'product_choice': item.product.product_choice,
                    'uom': {
                        'id': item.product.sale_information['default_uom']['id'],
                        'title': item.product.sale_information['default_uom']['title']
                    },
                    'uom_group': item.product.general_information['uom_group']['title'],
                    'tax_code': item.product.sale_information['tax_code']['id'],
                }
            }
            for item in so_product
        ]
