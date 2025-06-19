from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.promotion.models import Promotion
from apps.masterdata.saledata.models import Shipping, ExpenseItem, WareHouse
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.accounts import Account, AccountShippingAddress, AccountBillingAddress
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import QuotationProduct, QuotationLogistic, QuotationCost, QuotationExpense, \
    QuotationIndicatorConfig, QuotationIndicator, QuotationAppConfig
from apps.shared import PriceMsg, SaleMsg, DisperseModel, BaseMsg


class QuotationCommonCreate:

    @classmethod
    def create_product(cls, validated_data, instance):
        instance.quotation_product_quotation.all().delete()
        QuotationProduct.objects.bulk_create(
            [QuotationProduct(
                quotation=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **quotation_product,
            ) for quotation_product in validated_data['quotation_products_data']]
        )
        return True

    @classmethod
    def create_logistic(cls, validated_data, instance):
        old_logistic = QuotationLogistic.objects.filter(quotation=instance)
        if old_logistic:
            old_logistic.delete()
        QuotationLogistic.objects.create(
            **validated_data['quotation_logistic_data'],
            quotation=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
        )
        return True

    @classmethod
    def create_cost(cls, validated_data, instance):
        instance.quotation_cost_quotation.all().delete()
        QuotationCost.objects.bulk_create(
            [QuotationCost(
                quotation=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **quotation_cost,
            ) for quotation_cost in validated_data['quotation_costs_data']]
        )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
        instance.quotation_expense_quotation.all().delete()
        QuotationExpense.objects.bulk_create([
            QuotationExpense(quotation=instance, **quotation_expense)
            for quotation_expense in validated_data['quotation_expenses_data']
        ])
        return True

    @classmethod
    def create_indicator(cls, validated_data, instance):
        instance.quotation_indicator_quotation.all().delete()
        for quotation_indicator in validated_data['quotation_indicators_data']:
            indicator_id = quotation_indicator.get('indicator', {}).get('id')
            indicator_code = quotation_indicator.get('indicator', {}).get('code')
            if indicator_id:
                del quotation_indicator['indicator']
                QuotationIndicator.objects.create(
                    quotation=instance,
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    indicator_id=indicator_id,
                    code=indicator_code,
                    **quotation_indicator
                )
        return True

    @classmethod
    def create_quotation_sub_models(cls, validated_data, instance):
        # quotation tabs
        if 'quotation_products_data' in validated_data:
            cls.create_product(validated_data=validated_data, instance=instance)
        if 'quotation_logistic_data' in validated_data:
            cls.create_logistic(
                validated_data=validated_data,
                instance=instance
            )
        if 'quotation_costs_data' in validated_data:
            cls.create_cost(validated_data=validated_data, instance=instance)
        if 'quotation_expenses_data' in validated_data:
            cls.create_expense(validated_data=validated_data, instance=instance)
        # indicator tab
        if 'quotation_indicators_data' in validated_data:
            cls.create_indicator(
                validated_data=validated_data,
                instance=instance
            )
        return True


class QuotationCommonValidate:

    @classmethod
    def validate_customer_id(cls, value):
        try:
            return str(Account.objects.get_on_company(id=value).id)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            if value is None:
                return value
            return str(Opportunity.objects.get_on_company(id=value).id)
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_contact_id(cls, value):
        try:
            return str(Contact.objects.get_on_company(id=value).id)
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_payment_term_id(cls, value):
        try:
            if value is None:
                return None
            return str(PaymentTerm.objects.get_on_company(id=value).id)
        except PaymentTerm.DoesNotExist:
            raise serializers.ValidationError({'payment_term': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_product_id(cls, value):
        try:
            return str(Product.objects.get_on_company(id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        try:
            if value is None:
                return None
            return str(UnitOfMeasure.objects.get_on_company(id=value).id)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_tax_id(cls, value):
        try:
            return str(Tax.objects.get_on_company(id=value).id)
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_expense_id(cls, value):
        try:
            return str(Expense.objects.get_on_company(id=value).id)
        except Expense.DoesNotExist:
            raise serializers.ValidationError({'expense': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_expense_item_id(cls, value):
        try:
            return str(ExpenseItem.objects.get_on_company(id=value).id)
        except ExpenseItem.DoesNotExist:
            raise serializers.ValidationError({'expense_item': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_price_list(cls, value):
        if isinstance(value, list):
            price_list = Price.objects.filter_on_company(id__in=value)
            if price_list.count() == len(value):
                return [
                    {'id': str(price.id), 'title': price.title, 'code': price.code}
                    for price in price_list
                ]
            raise serializers.ValidationError({'price_list': PriceMsg.PRICE_LIST_IS_ARRAY})
        raise serializers.ValidationError({'price_list': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_promotion_id(cls, value):
        try:
            return str(Promotion.objects.get_on_company(id=value).id)
        except Promotion.DoesNotExist:
            raise serializers.ValidationError({'promotion': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_shipping_id(cls, value):
        try:
            return str(Shipping.objects.get_on_company(id=value).id)
        except Shipping.DoesNotExist:
            raise serializers.ValidationError({'shipping': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_indicator(cls, value):
        try:
            indicator = QuotationIndicatorConfig.objects.get_on_company(id=value)
            return {
                'id': str(indicator.id),
                'title': indicator.title,
                'code': indicator.code,
                'remark': indicator.remark
            }
        except QuotationIndicatorConfig.DoesNotExist:
            raise serializers.ValidationError({'indicator': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_customer_shipping(cls, value):
        try:
            return AccountShippingAddress.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer_shipping': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_customer_billing(cls, value):
        try:
            return AccountBillingAddress.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer_billing': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_on_company(id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_next_node_collab_id(cls, value):
        try:
            return Employee.objects.get_on_company(id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'next_node_collab': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_warehouse(cls, value):
        try:
            WareHouse.objects.get_on_company(id=value)
            return str(value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': BaseMsg.NOT_EXIST})


class QuotationValueValidate:
    @classmethod
    def validate_quantity(cls, value):
        if isinstance(value, float):
            if value > 0:
                return value
        raise serializers.ValidationError({'product_quantity': SaleMsg.QUANTITY_VALID})

    @classmethod
    def validate_price(cls, value):
        if isinstance(value, float):
            if value > 0:
                return value
        raise serializers.ValidationError({'product_price': SaleMsg.PRICE_VALID})


class QuotationRuleValidate:
    @classmethod
    def validate_config_role(cls, validate_data):
        if 'employee_inherit_id' in validate_data:
            opportunity_id = validate_data.get('opportunity_id', None)
            model_cls = DisperseModel(app_model="hr.employee").get_model()
            if model_cls and hasattr(model_cls, 'objects'):
                so_config = QuotationAppConfig.objects.filter_on_company().first()
                employee = model_cls.objects.filter(id=validate_data['employee_inherit_id']).first()
                if so_config and employee:
                    ss_role = [role.id for role in so_config.ss_role.all()]
                    ls_role = [role.id for role in so_config.ls_role.all()]
                    for role in employee.role.all():
                        if role.id in ss_role and opportunity_id:
                            raise serializers.ValidationError({'detail': SaleMsg.SO_CONFIG_SS_ROLE_CHECK})
                        if role.id in ls_role and not opportunity_id:
                            raise serializers.ValidationError({'detail': SaleMsg.SO_CONFIG_LS_ROLE_CHECK})
        return True

    @classmethod
    def validate_then_set_indicators_value(cls, validate_data):
        if 'quotation_indicators_data' in validate_data:
            for quotation_indicator in validate_data['quotation_indicators_data']:
                indicator_code = quotation_indicator.get('indicator', {}).get('code')
                indicator_value = quotation_indicator.get('indicator_value', 0)
                if indicator_code == 'IN0001':
                    validate_data.update({'indicator_revenue': indicator_value})
                elif indicator_code == 'IN0003':
                    validate_data.update({'indicator_gross_profit': indicator_value})
                elif indicator_code == 'IN0006':
                    validate_data.update({'indicator_net_income': indicator_value})
        return True


# SUB SERIALIZERS
class QuotationProductSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(allow_null=True, error_messages={
        'required': SaleMsg.PRODUCT_UOM_REQUIRED,
    })
    tax_id = serializers.UUIDField(required=False, allow_null=True)
    promotion_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = QuotationProduct
        fields = (
            'product_id',
            'product_data',
            'unit_of_measure_id',
            'uom_data',
            'tax_id',
            'tax_data',
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
            'product_discount_amount_total',
            'product_tax_title',
            'product_tax_value',
            'product_tax_amount',
            'product_subtotal_price',
            'product_subtotal_price_after_tax',
            'order',
            'is_promotion',
            'promotion_id',
            'promotion_data',
            'is_shipping',
            'shipping_id',
            'shipping_data',
            'is_group',
            'group_title',
            'group_order',
        )

    @classmethod
    def validate_product_id(cls, value):
        return QuotationCommonValidate().validate_product_id(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return QuotationCommonValidate().validate_unit_of_measure_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return QuotationCommonValidate().validate_tax_id(value=value)

    @classmethod
    def validate_promotion_id(cls, value):
        return QuotationCommonValidate().validate_promotion_id(value=value)

    @classmethod
    def validate_shipping_id(cls, value):
        return QuotationCommonValidate().validate_shipping_id(value=value)

    @classmethod
    def validate_product_quantity(cls, value):
        return QuotationValueValidate.validate_quantity(value=value)

    @classmethod
    def validate_product_unit_price(cls, value):
        return QuotationValueValidate.validate_price(value=value)


class QuotationLogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLogistic
        fields = (
            'shipping_address',
            'billing_address',
        )


class QuotationCostSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = QuotationCost
        fields = (
            'product_id',
            'product_data',
            'warehouse_id',
            'warehouse_data',
            'unit_of_measure_id',
            'uom_data',
            'tax_id',
            'tax_data',
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
            'shipping_id',
            'shipping_data',
            'supplied_by',
        )

    @classmethod
    def validate_product_id(cls, value):
        return QuotationCommonValidate().validate_product_id(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return QuotationCommonValidate().validate_unit_of_measure_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return QuotationCommonValidate().validate_tax_id(value=value)

    @classmethod
    def validate_shipping_id(cls, value):
        return QuotationCommonValidate().validate_shipping_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return QuotationCommonValidate().validate_warehouse(value=value)

    # @classmethod
    # def validate_product_quantity(cls, value):
    #     return QuotationValueValidate.validate_quantity(value=value)


class QuotationExpenseSerializer(serializers.ModelSerializer):
    expense_id = serializers.UUIDField(required=False, allow_null=True)
    expense_item_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(error_messages={
        'required': SaleMsg.EXPENSE_UOM_REQUIRED,
    })
    tax_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = QuotationExpense
        fields = (
            'expense_id',
            'expense_data',
            'expense_item_id',
            'expense_item_data',
            'unit_of_measure_id',
            'uom_data',
            'tax_id',
            'tax_data',
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
    def validate_expense_id(cls, value):
        return QuotationCommonValidate().validate_expense_id(value=value)

    @classmethod
    def validate_expense_item_id(cls, value):
        return QuotationCommonValidate().validate_expense_item_id(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return QuotationCommonValidate().validate_unit_of_measure_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return QuotationCommonValidate().validate_tax_id(value=value)


class QuotationIndicatorSerializer(serializers.ModelSerializer):
    indicator = serializers.UUIDField()

    class Meta:
        model = QuotationIndicator
        fields = (
            'indicator',
            'indicator_data',
            'indicator_value',
            'indicator_rate',
            'order',
        )

    @classmethod
    def validate_indicator(cls, value):
        return QuotationCommonValidate().validate_indicator(value=value)
