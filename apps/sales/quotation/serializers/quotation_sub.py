from apps.sales.quotation.models import QuotationProduct, QuotationTerm, QuotationTermPrice, \
    QuotationTermDiscount, QuotationLogistic, QuotationLogisticShipping, QuotationLogisticBilling, QuotationCost, \
    QuotationExpense


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
    def create_product(cls, validated_data, instance):
        for quotation_product in validated_data['quotation_products_data']:
            product_id, unit_of_measure_id, tax_id = cls.validate_product_cost(dict_data=quotation_product)
            QuotationProduct.objects.create(
                quotation=instance,
                product_id=product_id,
                unit_of_measure_id=unit_of_measure_id,
                tax_id=tax_id,
                **quotation_product
            )
        return True

    @classmethod
    def create_term(cls, validated_data, instance):
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
    def create_logistic(cls, validated_data, instance):
        shipping_address_list = []
        billing_address_list = []
        if 'shipping_address_list' in validated_data['quotation_logistic_data']:
            shipping_address_list = validated_data['quotation_logistic_data']['shipping_address_list']
            del validated_data['quotation_logistic_data']['shipping_address_list']
        if 'billing_address_list' in validated_data['quotation_logistic_data']:
            billing_address_list = validated_data['quotation_logistic_data']['billing_address_list']
            del validated_data['quotation_logistic_data']['billing_address_list']
        quotation_logistic = QuotationLogistic.objects.create(quotation=instance)
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
    def create_cost(cls, validated_data, instance):
        for quotation_cost in validated_data['quotation_costs_data']:
            product_id, unit_of_measure_id, tax_id = cls.validate_product_cost(dict_data=quotation_cost)
            QuotationCost.objects.create(
                quotation=instance,
                product_id=product_id,
                unit_of_measure_id=unit_of_measure_id,
                tax_id=tax_id,
                **quotation_cost
            )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
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
                quotation=instance,
                expense_id=expense_id,
                unit_of_measure_id=unit_of_measure_id,
                tax_id=tax_id,
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

    @classmethod
    def delete_old_logistic(cls, instance):
        old_logistic = QuotationLogistic.objects.filter(quotation=instance)
        if old_logistic:
            old_logistic_shipping = QuotationLogisticShipping.objects.filter(
                quotation_logistic__in=old_logistic
            )
            if old_logistic_shipping:
                old_logistic_shipping.delete()
            old_logistic_billing = QuotationLogisticBilling.objects.filter(
                quotation_logistic__in=old_logistic
            )
            if old_logistic_billing:
                old_logistic_billing.delete()
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
