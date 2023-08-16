from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.promotion.models import Promotion
from apps.masterdata.saledata.models import Shipping
from apps.masterdata.saledata.models.accounts import Account, Contact, AccountShippingAddress, AccountBillingAddress
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderLogistic, SaleOrderCost, SaleOrderExpense, \
    SaleOrderIndicatorConfig, SaleOrderIndicator
from apps.sales.quotation.serializers import QuotationCommonValidate
from apps.masterdata.saledata.serializers import ProductForSaleListSerializer
from apps.shared import AccountsMsg, ProductMsg, PriceMsg, SaleMsg, HRMsg, PromoMsg, ShippingMsg


class SaleOrderCommonCreate:

    @classmethod
    def validate_product_cost_expense(cls, dict_data, is_product=False, is_expense=False, is_cost=False):
        product = {}
        expense = {}
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
                    product_id=data['product'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    **sale_order_expense
                )
        return True

    @classmethod
    def create_indicator(cls, validated_data, instance):
        for sale_order_indicator in validated_data['sale_order_indicators_data']:
            # indicator_id = sale_order_indicator.get('indicator', {}).get('id')
            quotation_indicator_id = sale_order_indicator.get('quotation_indicator', {}).get('id')
            # if indicator_id:
            if quotation_indicator_id:
                # del sale_order_indicator['indicator']
                del sale_order_indicator['quotation_indicator']
                SaleOrderIndicator.objects.create(
                    sale_order=instance,
                    # indicator_id=indicator_id,
                    quotation_indicator_id=quotation_indicator_id,
                    **sale_order_indicator
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
            )
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
            return {
                'id': str(product.id),
                'title': product.title,
                'code': product.code,
                'product_choice': product.product_choice,
            }
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
                'code': promotion.code
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
    def validate_employee_inherit(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': HRMsg.EMPLOYEES_NOT_EXIST})


# SUB SERIALIZERS
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