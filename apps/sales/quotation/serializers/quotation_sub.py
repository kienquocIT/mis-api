from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.promotion.models import Promotion
from apps.masterdata.saledata.models import Shipping
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import QuotationProduct, QuotationTerm, QuotationTermPrice, \
    QuotationTermDiscount, QuotationLogistic, QuotationCost, QuotationExpense, Indicator, QuotationIndicator
from apps.shared import AccountsMsg, ProductMsg, PriceMsg, SaleMsg, HRMsg, ShippingMsg, PromoMsg


class QuotationCommonCreate:

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
        for quotation_product in validated_data['quotation_products_data']:
            data = cls.validate_product_cost_expense(
                dict_data=quotation_product,
                is_product=True
            )
            if data:
                QuotationProduct.objects.create(
                    quotation=instance,
                    product_id=data['product'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    promotion_id=data['promotion'].get('id', None),
                    shipping_id=data['shipping'].get('id', None),
                    **quotation_product
                )
        return True

    @classmethod
    def create_term(cls, validated_data, instance):
        price_list = []
        payment_term = {}
        if 'price_list' in validated_data['quotation_term_data']:
            price_list = validated_data['quotation_term_data']['price_list']
            del validated_data['quotation_term_data']['price_list']
        if 'payment_term' in validated_data['quotation_term_data']:
            payment_term = validated_data['quotation_term_data']['payment_term']
            del validated_data['quotation_term_data']['payment_term']
        quotation_term = QuotationTerm.objects.create(
            payment_term_id=payment_term.get('id', None),
            quotation=instance
        )
        if price_list:
            QuotationTermPrice.objects.bulk_create([
                QuotationTermPrice(
                    price_id=price.get('id', None),
                    quotation_term=quotation_term
                )
                for price in price_list
            ])
        return True

    @classmethod
    def create_logistic(cls, validated_data, instance):
        QuotationLogistic.objects.create(
            **validated_data['quotation_logistic_data'],
            quotation=instance
        )
        return True

    @classmethod
    def create_cost(cls, validated_data, instance):
        for quotation_cost in validated_data['quotation_costs_data']:
            data = cls.validate_product_cost_expense(
                dict_data=quotation_cost,
                is_cost=True
            )
            if data:
                QuotationCost.objects.create(
                    quotation=instance,
                    product_id=data['product'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    shipping_id=data['shipping'].get('id', None),
                    **quotation_cost
                )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
        for quotation_expense in validated_data['quotation_expenses_data']:
            data = cls.validate_product_cost_expense(
                dict_data=quotation_expense,
                is_expense=True
            )
            if data:
                QuotationExpense.objects.create(
                    quotation=instance,
                    expense_id=data['expense'].get('id', None),
                    unit_of_measure_id=data['unit_of_measure'].get('id', None),
                    tax_id=data['tax'].get('id', None),
                    **quotation_expense
                )
        return True

    @classmethod
    def create_indicator(cls, validated_data, instance):
        for quotation_indicator in validated_data['quotation_indicators_data']:
            indicator_id = quotation_indicator.get('indicator', {}).get('id')
            if indicator_id:
                del quotation_indicator['indicator']
                QuotationIndicator.objects.create(
                    quotation=instance,
                    indicator_id=indicator_id,
                    **quotation_indicator
                )
        return True

    @classmethod
    def delete_old_product(cls, instance):
        old_product = QuotationProduct.objects.filter(quotation=instance)
        if old_product:
            old_product.delete()
        return True

    @classmethod
    def delete_old_term(cls, instance):
        old_term = QuotationTerm.objects.filter(quotation=instance)
        if old_term:
            old_term_price = QuotationTermPrice.objects.filter(quotation_term__in=old_term)
            if old_term_price:
                old_term_price.delete()
            old_term_discount = QuotationTermDiscount.objects.filter(quotation_term__in=old_term)
            if old_term_discount:
                old_term_discount.delete()
        return True

    @classmethod
    def delete_old_logistic(cls, instance):
        old_logistic = QuotationLogistic.objects.filter(quotation=instance)
        if old_logistic:
            old_logistic.delete()
        return True

    @classmethod
    def delete_old_cost(cls, instance):
        old_cost = QuotationCost.objects.filter(quotation=instance)
        if old_cost:
            old_cost.delete()
        return True

    @classmethod
    def delete_old_expense(cls, instance):
        old_expense = QuotationExpense.objects.filter(quotation=instance)
        if old_expense:
            old_expense.delete()
        return True

    @classmethod
    def delete_old_indicator(cls, instance):
        old_indicator = QuotationIndicator.objects.filter(quotation=instance)
        if old_indicator:
            old_indicator.delete()
        return True

    @classmethod
    def create_quotation_sub_models(cls, validated_data, instance, is_update=False):
        # quotation tabs
        if 'quotation_products_data' in validated_data:
            if is_update is True:
                cls.delete_old_product(instance=instance)
            cls.create_product(
                validated_data=validated_data,
                instance=instance
            )
        if 'quotation_term_data' in validated_data:
            if is_update is True:
                cls.delete_old_term(instance=instance)
            cls.create_term(
                validated_data=validated_data,
                instance=instance
            )
        if 'quotation_logistic_data' in validated_data:
            if is_update is True:
                cls.delete_old_logistic(instance=instance)
            cls.create_logistic(
                validated_data=validated_data,
                instance=instance
            )
        if 'quotation_costs_data' in validated_data:
            if is_update is True:
                cls.delete_old_cost(instance=instance)
            cls.create_cost(
                validated_data=validated_data,
                instance=instance
            )
        if 'quotation_expenses_data' in validated_data:
            if is_update is True:
                cls.delete_old_expense(instance=instance)
            cls.create_expense(
                validated_data=validated_data,
                instance=instance
            )
        # indicator tab
        if 'quotation_indicators_data' in validated_data:
            if is_update is True:
                cls.delete_old_indicator(instance=instance)
            cls.create_indicator(
                validated_data=validated_data,
                instance=instance
            )
        return True


class QuotationCommonValidate:

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
            raise serializers.ValidationError({'employee': HRMsg.EMPLOYEES_NOT_EXIST})

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
                'code': product.code
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
                'value': tax.rate
            }
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': ProductMsg.TAX_DOES_NOT_EXIST})

    @classmethod
    def validate_expense(cls, value):
        try:
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
            raise serializers.ValidationError({'payment_term': AccountsMsg.PAYMENT_TERM_NOT_EXIST})

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
            indicator = Indicator.objects.get_current(
                fill__company=True,
                id=value
            )
            return {
                'id': str(indicator.id),
                'title': indicator.title,
                'code': indicator.remark
            }
        except Indicator.DoesNotExist:
            raise serializers.ValidationError({'indicator': ProductMsg.PRODUCT_DOES_NOT_EXIST})
