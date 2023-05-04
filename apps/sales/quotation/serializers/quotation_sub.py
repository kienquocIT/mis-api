from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.accounts import Account, Contact
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import QuotationProduct, QuotationTerm, QuotationTermPrice, \
    QuotationTermDiscount, QuotationLogistic, QuotationCost, QuotationExpense
from apps.shared import AccountsMsg, ProductMsg, PriceMsg, SaleMsg, HRMsg


class QuotationCommonCreate:

    @classmethod
    def validate_product_cost_expense(cls, dict_data, is_expense=False):
        product = {}
        expense = {}
        unit_of_measure = {}
        tax = {}
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
        if is_expense is True:
            return expense, unit_of_measure, tax
        return product, unit_of_measure, tax

    @classmethod
    def create_product(cls, validated_data, instance):
        for quotation_product in validated_data['quotation_products_data']:
            product, unit_of_measure, tax = cls.validate_product_cost_expense(dict_data=quotation_product)
            QuotationProduct.objects.create(
                quotation=instance,
                product_id=product.get('id', None),
                unit_of_measure_id=unit_of_measure.get('id', None),
                tax_id=tax.get('id', None),
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

    # @classmethod
    # def create_logistic(cls, validated_data, instance):
    #     shipping_address_list = []
    #     billing_address_list = []
    #     if 'shipping_address_list' in validated_data['quotation_logistic_data']:
    #         shipping_address_list = validated_data['quotation_logistic_data']['shipping_address_list']
    #         del validated_data['quotation_logistic_data']['shipping_address_list']
    #     if 'billing_address_list' in validated_data['quotation_logistic_data']:
    #         billing_address_list = validated_data['quotation_logistic_data']['billing_address_list']
    #         del validated_data['quotation_logistic_data']['billing_address_list']
    #     quotation_logistic = QuotationLogistic.objects.create(quotation=instance)
    #     if shipping_address_list:
    #         QuotationLogisticShipping.objects.bulk_create([
    #             QuotationLogisticShipping(
    #                 shipping_address_id=shipping_address.get('id', None),
    #                 quotation_logistic=quotation_logistic
    #             )
    #             for shipping_address in shipping_address_list
    #         ])
    #     if billing_address_list:
    #         QuotationLogisticBilling.objects.bulk_create([
    #             QuotationLogisticBilling(
    #                 billing_address_id=billing_address.get('id', None),
    #                 quotation_logistic=quotation_logistic
    #             )
    #             for billing_address in billing_address_list
    #         ])
    #     return True

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
            product, unit_of_measure, tax = cls.validate_product_cost_expense(dict_data=quotation_cost)
            QuotationCost.objects.create(
                quotation=instance,
                product_id=product.get('id', None),
                unit_of_measure_id=unit_of_measure.get('id', None),
                tax_id=tax.get('id', None),
                **quotation_cost
            )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
        for quotation_expense in validated_data['quotation_expenses_data']:
            expense, unit_of_measure, tax = cls.validate_product_cost_expense(
                dict_data=quotation_expense,
                is_expense=True
            )
            QuotationExpense.objects.create(
                quotation=instance,
                expense_id=expense.get('id', None),
                unit_of_measure_id=unit_of_measure.get('id', None),
                tax_id=tax.get('id', None),
                **quotation_expense
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

    # @classmethod
    # def delete_old_logistic(cls, instance):
    #     old_logistic = QuotationLogistic.objects.filter(quotation=instance)
    #     if old_logistic:
    #         old_logistic_shipping = QuotationLogisticShipping.objects.filter(
    #             quotation_logistic__in=old_logistic
    #         )
    #         if old_logistic_shipping:
    #             old_logistic_shipping.delete()
    #         old_logistic_billing = QuotationLogisticBilling.objects.filter(
    #             quotation_logistic__in=old_logistic
    #         )
    #         if old_logistic_billing:
    #             old_logistic_billing.delete()
    #         old_logistic.delete()
    #     return True

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
    def create_quotation_sub_models(cls, validated_data, instance, is_update=False):
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
            raise serializers.ValidationError({'expense': ProductMsg.PRODUCT_DOES_NOT_EXIST})

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

    # @classmethod
    # def validate_payment_term(cls, value):
    #     try:
    #         payment = PaymentTerm.objects.get_current(
    #             fill__tenant=True,
    #             fill__company=True,
    #             id=value
    #         )
    #         return {
    #             'id': str(payment.id),
    #             'title': payment.title,
    #             'code': payment.code
    #         }
    #     except PaymentTerm.DoesNotExist:
    #         raise serializers.ValidationError({'payment_term': ProductMsg.PRODUCT_DOES_NOT_EXIST})

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
