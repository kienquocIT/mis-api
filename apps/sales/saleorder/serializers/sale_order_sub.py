from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.accounts import Account, Contact
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderLogistic, SaleOrderCost, SaleOrderExpense
from apps.shared import AccountsMsg, ProductMsg, PriceMsg, SaleMsg, HRMsg


class SaleOrderCommonCreate:

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
        for sale_order_product in validated_data['sale_order_products_data']:
            product, unit_of_measure, tax = cls.validate_product_cost_expense(dict_data=sale_order_product)
            SaleOrderProduct.objects.create(
                sale_order=instance,
                product_id=product.get('id', None),
                unit_of_measure_id=unit_of_measure.get('id', None),
                tax_id=tax.get('id', None),
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
            product, unit_of_measure, tax = cls.validate_product_cost_expense(dict_data=sale_order_cost)
            SaleOrderCost.objects.create(
                sale_order=instance,
                product_id=product.get('id', None),
                unit_of_measure_id=unit_of_measure.get('id', None),
                tax_id=tax.get('id', None),
                **sale_order_cost
            )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
        for sale_order_expense in validated_data['sale_order_expenses_data']:
            expense, unit_of_measure, tax = cls.validate_product_cost_expense(
                dict_data=sale_order_expense,
                is_expense=True
            )
            SaleOrderExpense.objects.create(
                sale_order=instance,
                expense_id=expense.get('id', None),
                unit_of_measure_id=unit_of_measure.get('id', None),
                tax_id=tax.get('id', None),
                **sale_order_expense
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
