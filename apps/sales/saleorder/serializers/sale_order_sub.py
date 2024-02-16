from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.promotion.models import Promotion
from apps.masterdata.saledata.models import Shipping, ExpenseItem
from apps.masterdata.saledata.models.accounts import Account, Contact, AccountShippingAddress, AccountBillingAddress
from apps.masterdata.saledata.models.config import PaymentTerm, Term
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderLogistic, SaleOrderCost, SaleOrderExpense, \
    SaleOrderIndicatorConfig, SaleOrderIndicator, SaleOrderPaymentStage
from apps.sales.quotation.serializers import QuotationCommonValidate
from apps.masterdata.saledata.serializers import ProductForSaleListSerializer
from apps.shared import AccountsMsg, ProductMsg, PriceMsg, SaleMsg, HRMsg, PromoMsg, ShippingMsg, APIMsg
from apps.shared.translations.expense import ExpenseMsg


class SaleOrderCommonCreate:

    @classmethod
    def validate_product_cost_expense(cls, dict_data, is_product=False, is_expense=False, is_cost=False):
        product = {}
        expense = {}
        expense_item = {}
        unit_of_measure = {}
        tax = {}
        promotion = {}
        shipping = {}
        if 'product' in dict_data:
            product = dict_data['product']
            del dict_data['product']
        if 'expense' in dict_data:
            expense = dict_data['expense']
            del dict_data['expense']
        if 'expense_item' in dict_data:
            expense_item = dict_data['expense_item']
            del dict_data['expense_item']
        if 'unit_of_measure' in dict_data:
            unit_of_measure = dict_data['unit_of_measure']
            del dict_data['unit_of_measure']
        if 'tax' in dict_data:
            tax = dict_data['tax']
            del dict_data['tax']
        if 'promotion' in dict_data:
            promotion = dict_data['promotion']
            del dict_data['promotion']
        if 'shipping' in dict_data:
            shipping = dict_data['shipping']
            del dict_data['shipping']
        if is_product is True:
            return {
                'product': product,
                'unit_of_measure': unit_of_measure,
                'tax': tax,
                'promotion': promotion,
                'shipping': shipping
            }
        if is_expense is True:
            return {
                'expense': expense,
                'expense_item': expense_item,
                'product': product,
                'unit_of_measure': unit_of_measure,
                'tax': tax,
            }
        if is_cost is True:
            return {
                'product': product,
                'unit_of_measure': unit_of_measure,
                'tax': tax,
                'shipping': shipping
            }
        return {}

    @classmethod
    def create_product(cls, validated_data, instance):
        for sale_order_product in validated_data['sale_order_products_data']:
            data = cls.validate_product_cost_expense(
                dict_data=sale_order_product,
                is_product=True
            )
            if data:
                SaleOrderProduct.objects.create(
                    sale_order=instance,
                    product_id=data['product'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    promotion_id=data['promotion'].get('id', None),
                    shipping_id=data['shipping'].get('id', None),
                    remain_for_purchase_request=sale_order_product.get('product_quantity', 0),
                    remain_for_purchase_order=sale_order_product.get('product_quantity', 0),
                    **sale_order_product
                )
        return True

    @classmethod
    def create_logistic(cls, validated_data, instance):
        SaleOrderLogistic.objects.create(
            **validated_data['sale_order_logistic_data'],
            sale_order=instance
        )
        return True

    @classmethod
    def create_cost(cls, validated_data, instance):
        for sale_order_cost in validated_data['sale_order_costs_data']:
            data = cls.validate_product_cost_expense(
                dict_data=sale_order_cost,
                is_cost=True
            )
            if data:
                SaleOrderCost.objects.create(
                    sale_order=instance,
                    product_id=data['product'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    shipping_id=data['shipping'].get('id', None),
                    **sale_order_cost
                )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
        for sale_order_expense in validated_data['sale_order_expenses_data']:
            data = cls.validate_product_cost_expense(
                dict_data=sale_order_expense,
                is_expense=True
            )
            if data:
                SaleOrderExpense.objects.create(
                    sale_order=instance,
                    expense_id=data['expense'].get('id', None),
                    expense_item_id=data['expense_item'].get('id', None),
                    product_id=data['product'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    **sale_order_expense
                )
        return True

    @classmethod
    def create_indicator(cls, validated_data, instance):
        for sale_order_indicator in validated_data['sale_order_indicators_data']:
            # indicator_id = sale_order_indicator.get('indicator', {}).get('id')
            quotation_indicator_id = sale_order_indicator.get('quotation_indicator', {}).get('id')
            quotation_indicator_code = sale_order_indicator.get('quotation_indicator', {}).get('code')
            # if indicator_id:
            if quotation_indicator_id:
                # del sale_order_indicator['indicator']
                del sale_order_indicator['quotation_indicator']
                SaleOrderIndicator.objects.create(
                    sale_order=instance,
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    # indicator_id=indicator_id,
                    quotation_indicator_id=quotation_indicator_id,
                    code=quotation_indicator_code,
                    **sale_order_indicator
                )
        return True

    @classmethod
    def create_payment_stage(cls, validated_data, instance):
        SaleOrderPaymentStage.objects.bulk_create(
            [SaleOrderPaymentStage(
                sale_order=instance,
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                **sale_order_payment_stage,
            ) for sale_order_payment_stage in validated_data['sale_order_payment_stage']]
        )
        return True

    @classmethod
    def delete_old_product(cls, instance):
        old_product = SaleOrderProduct.objects.filter(sale_order=instance)
        if old_product:
            old_product.delete()
        return True

    @classmethod
    def delete_old_logistic(cls, instance):
        old_logistic = SaleOrderLogistic.objects.filter(sale_order=instance)
        if old_logistic:
            old_logistic.delete()
        return True

    @classmethod
    def delete_old_cost(cls, instance):
        old_cost = SaleOrderCost.objects.filter(sale_order=instance)
        if old_cost:
            old_cost.delete()
        return True

    @classmethod
    def delete_old_expense(cls, instance):
        old_expense = SaleOrderExpense.objects.filter(sale_order=instance)
        if old_expense:
            old_expense.delete()
        return True

    @classmethod
    def delete_old_indicator(cls, instance):
        old_indicator = SaleOrderIndicator.objects.filter(sale_order=instance)
        if old_indicator:
            old_indicator.delete()
        return True

    @classmethod
    def delete_old_payment_stage(cls, instance):
        old_payment_stage = SaleOrderPaymentStage.objects.filter(sale_order=instance)
        if old_payment_stage:
            old_payment_stage.delete()
        return True

    @classmethod
    def create_sale_order_sub_models(cls, validated_data, instance, is_update=False):
        if 'sale_order_products_data' in validated_data:
            if is_update is True:
                cls.delete_old_product(instance=instance)
            cls.create_product(
                validated_data=validated_data,
                instance=instance
            )
        if 'sale_order_logistic_data' in validated_data:
            if is_update is True:
                cls.delete_old_logistic(instance=instance)
            cls.create_logistic(
                validated_data=validated_data,
                instance=instance
            )
        if 'sale_order_costs_data' in validated_data:
            if is_update is True:
                cls.delete_old_cost(instance=instance)
            cls.create_cost(
                validated_data=validated_data,
                instance=instance
            )
        if 'sale_order_expenses_data' in validated_data:
            if is_update is True:
                cls.delete_old_expense(instance=instance)
            cls.create_expense(
                validated_data=validated_data,
                instance=instance
            )
        # indicator tab
        if 'sale_order_indicators_data' in validated_data:
            if is_update is True:
                cls.delete_old_indicator(instance=instance)
            cls.create_indicator(
                validated_data=validated_data,
                instance=instance
            )
        # payment stage tab
        if 'sale_order_payment_stage' in validated_data:
            if is_update is True:
                cls.delete_old_payment_stage(instance=instance)
            cls.create_payment_stage(
                validated_data=validated_data,
                instance=instance
            )
        return True


class SaleOrderCommonValidate:

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

    @classmethod
    def validate_opportunity(cls, value):
        try:
            if value is None:
                return value
            return Opportunity.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            ).id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': SaleMsg.OPPORTUNITY_NOT_EXIST})

    @classmethod
    def validate_contact(cls, value):
        try:
            return Contact.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': AccountsMsg.CONTACT_NOT_EXIST})

    @classmethod
    def validate_sale_person(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'sale_person': HRMsg.EMPLOYEES_NOT_EXIST})

    @classmethod
    def validate_quotation(cls, value):
        try:
            return Quotation.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Quotation.DoesNotExist:
            raise serializers.ValidationError({'quotation': SaleMsg.QUOTATION_NOT_EXIST})

    @classmethod
    def validate_product(cls, value):
        try:
            if value is None:
                return {}
            product = Product.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return ProductForSaleListSerializer(product).data
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_unit_of_measure(cls, value):
        try:
            if value is None:
                return {}
            uom = UnitOfMeasure.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(uom.id),
                'title': uom.title,
                'code': uom.code
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        try:
            tax = Tax.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(tax.id),
                'title': tax.title,
                'code': tax.code,
                'rate': tax.rate
            }
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': ProductMsg.TAX_DOES_NOT_EXIST})

    @classmethod
    def validate_expense(cls, value):
        try:
            if value is None:
                return {}
            expense = Expense.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(expense.id),
                'title': expense.title,
                'code': expense.code
            }
        except Expense.DoesNotExist:
            raise serializers.ValidationError({'expense': ProductMsg.EXPENSE_DOES_NOT_EXIST})

    @classmethod
    def validate_expense_item(cls, value):
        try:
            if value is None:
                return {}
            expense_item = ExpenseItem.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(expense_item.id),
                'title': expense_item.title,
                'code': expense_item.code
            }
        except ExpenseItem.DoesNotExist:
            raise serializers.ValidationError({'expense_item': ExpenseMsg.EXPENSE_ITEM_NOT_EXIST})

    @classmethod
    def validate_price_list(cls, value):
        if isinstance(value, list):
            price_list = Price.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=value
            )
            if price_list.count() == len(value):
                return [
                    {'id': str(price.id), 'title': price.title, 'code': price.code}
                    for price in price_list
                ]
            raise serializers.ValidationError({'price_list': PriceMsg.PRICE_LIST_IS_ARRAY})
        raise serializers.ValidationError({'price_list': PriceMsg.PRICE_LIST_NOT_EXIST})

    @classmethod
    def validate_payment_term(cls, value):
        try:
            return PaymentTerm.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except PaymentTerm.DoesNotExist:
            raise serializers.ValidationError({'payment_term': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_promotion(cls, value):
        try:
            if value is None:
                return {}
            promotion = Promotion.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(promotion.id),
                'title': promotion.title,
                'code': promotion.code,
                'valid_date_start': promotion.valid_date_start,
                'valid_date_end': promotion.valid_date_end,
                'remark': promotion.remark,
                'currency': {
                    'id': str(promotion.currency_id),
                    'title': promotion.currency.title,
                    'abbreviation': promotion.currency.abbreviation,
                } if promotion.currency else {},
                'customer_type': promotion.customer_type,
                'customer_by_list': promotion.customer_by_list,
                'customer_by_condition': promotion.customer_by_condition,
                'customer_remark': promotion.customer_remark,
                'is_discount': promotion.is_discount,
                'is_gift': promotion.is_gift,
                'discount_method': promotion.discount_method,
                'gift_method': promotion.gift_method,
                'sale_order_used': [
                    {
                        'customer_id': order_used[0],
                        'date_created': order_used[1],
                    } for order_used in promotion.sale_order_product_promotion.values_list(
                        'sale_order__customer_id',
                        'sale_order__date_created'
                    )
                ]
            }
        except Promotion.DoesNotExist:
            raise serializers.ValidationError({'promotion': PromoMsg.PROMOTION_NOT_EXIST})

    @classmethod
    def validate_shipping(cls, value):
        try:
            if value is None:
                return {}
            shipping = Shipping.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return {
                'id': str(shipping.id),
                'title': shipping.title,
                'code': shipping.code
            }
        except Shipping.DoesNotExist:
            raise serializers.ValidationError({'shipping': ShippingMsg.SHIPPING_NOT_EXIST})

    @classmethod
    def validate_indicator(cls, value):
        try:
            indicator = SaleOrderIndicatorConfig.objects.get_current(
                fill__company=True,
                id=value
            )
            return {
                'id': str(indicator.id),
                'title': indicator.title,
                'remark': indicator.remark
            }
        except SaleOrderIndicatorConfig.DoesNotExist:
            raise serializers.ValidationError({'indicator': ProductMsg.INDICATOR_NOT_EXIST})

    @classmethod
    def validate_customer_shipping(cls, value):
        try:
            return AccountShippingAddress.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer_shipping': AccountsMsg.ACCOUNT_SHIPPING_NOT_EXIST})

    @classmethod
    def validate_customer_billing(cls, value):
        try:
            return AccountBillingAddress.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer_billing': AccountsMsg.ACCOUNT_BILLING_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            ).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': HRMsg.EMPLOYEES_NOT_EXIST})

    @classmethod
    def validate_then_set_indicators_value(cls, validate_data):
        if 'sale_order_indicators_data' in validate_data:
            for so_indicator in validate_data['sale_order_indicators_data']:
                indicator_code = so_indicator.get('quotation_indicator', {}).get('code')
                indicator_value = so_indicator.get('indicator_value', 0)
                if indicator_code == 'IN0001':
                    validate_data.update({'indicator_revenue': indicator_value})
                elif indicator_code == 'IN0003':
                    validate_data.update({'indicator_gross_profit': indicator_value})
                elif indicator_code == 'IN0006':
                    validate_data.update({'indicator_net_income': indicator_value})
        return True

    @classmethod
    def validate_term_id(cls, value):
        try:
            return str(Term.objects.get(id=value).id)
        except Term.DoesNotExist:
            raise serializers.ValidationError({'term': AccountsMsg.PAYMENT_TERM_NOT_EXIST})

    @classmethod
    def validate_total_payment_term(cls, validate_data):
        if 'sale_order_payment_stage' in validate_data:
            total = 0
            for payment_stage in validate_data['sale_order_payment_stage']:
                total += payment_stage.get('payment_ratio', 0)
            if total < 100:
                raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
        return True


# SUB SERIALIZERS
class SaleOrderProductSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(
        allow_null=True
    )
    unit_of_measure = serializers.UUIDField()
    tax = serializers.UUIDField(
        required=False
    )
    promotion = serializers.UUIDField(
        allow_null=True
    )
    shipping = serializers.UUIDField(
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


class SaleOrderProductsListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    unit_of_measure = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    promotion = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()

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
    def get_product(cls, obj):
        return ProductForSaleListSerializer(obj.product).data

    @classmethod
    def get_unit_of_measure(cls, obj):
        return {
            'id': obj.unit_of_measure_id,
            'title': obj.unit_of_measure.title,
            'code': obj.unit_of_measure.code
        } if obj.unit_of_measure else {}

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}

    @classmethod
    def get_promotion(cls, obj):
        return {
            'id': obj.promotion_id,
            'title': obj.promotion.title,
            'code': obj.promotion.code
        } if obj.promotion else {}

    @classmethod
    def get_shipping(cls, obj):
        return {
            'id': obj.shipping_id,
            'title': obj.shipping.title,
            'code': obj.shipping.code
        } if obj.shipping else {}


class SaleOrderLogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderLogistic
        fields = (
            'shipping_address',
            'billing_address',
        )


class SaleOrderCostSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(
        allow_null=True
    )
    unit_of_measure = serializers.UUIDField(
        allow_null=True
    )
    tax = serializers.UUIDField(
        required=False
    )
    shipping = serializers.UUIDField(
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


class SaleOrderCostsListSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    unit_of_measure = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()

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
    def get_product(cls, obj):
        return ProductForSaleListSerializer(obj.product).data

    @classmethod
    def get_unit_of_measure(cls, obj):
        return {
            'id': obj.unit_of_measure_id,
            'title': obj.unit_of_measure.title,
            'code': obj.unit_of_measure.code
        } if obj.unit_of_measure else {}

    @classmethod
    def get_tax(cls, obj):
        return {
            'id': obj.tax_id,
            'title': obj.tax.title,
            'code': obj.tax.code,
            'rate': obj.tax.rate,
        } if obj.tax else {}

    @classmethod
    def get_shipping(cls, obj):
        return {
            'id': obj.shipping_id,
            'title': obj.shipping.title,
            'code': obj.shipping.code
        } if obj.shipping else {}


class SaleOrderExpenseSerializer(serializers.ModelSerializer):
    expense = serializers.UUIDField(
        allow_null=True,
        required=False,
    )
    expense_item = serializers.UUIDField(
        allow_null=True,
    )
    product = serializers.UUIDField(
        allow_null=True,
        required=False,
    )
    unit_of_measure = serializers.UUIDField()
    tax = serializers.UUIDField(
        required=False
    )

    class Meta:
        model = SaleOrderExpense
        fields = (
            'expense',
            'expense_item',
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
            'is_labor',
        )

    @classmethod
    def validate_expense(cls, value):
        return SaleOrderCommonValidate().validate_expense(value=value)

    @classmethod
    def validate_expense_item(cls, value):
        return SaleOrderCommonValidate().validate_expense_item(value=value)

    @classmethod
    def validate_product(cls, value):
        return SaleOrderCommonValidate().validate_product(value=value)

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
    quotation_indicator = serializers.UUIDField()

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


class SaleOrderPaymentStageSerializer(serializers.ModelSerializer):
    term_id = serializers.UUIDField(required=False, allow_null=True)
    date = serializers.CharField(required=False, allow_null=True)
    due_date = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = SaleOrderPaymentStage
        fields = (
            'remark',
            'term_id',
            'term_data',
            'date',
            'payment_ratio',
            'value_before_tax',
            'due_date',
            'is_ar_invoice',
            'order',
        )

    @classmethod
    def validate_remark(cls, value):
        if not value:
            raise serializers.ValidationError({'remark': APIMsg.FIELD_REQUIRED})
        return value

    @classmethod
    def validate_term_id(cls, value):
        return SaleOrderCommonValidate().validate_term_id(value=value)
