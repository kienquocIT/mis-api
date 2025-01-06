from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.promotion.models import Promotion
from apps.masterdata.saledata.models import Shipping, ExpenseItem, WareHouse
from apps.masterdata.saledata.models.accounts import Account, Contact, AccountShippingAddress, AccountBillingAddress
from apps.masterdata.saledata.models.config import PaymentTerm, Term
from apps.masterdata.saledata.models.price import Tax, Price
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, Expense
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation, QuotationAppConfig
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderLogistic, SaleOrderCost, SaleOrderExpense, \
    SaleOrderIndicatorConfig, SaleOrderIndicator, SaleOrderPaymentStage
from apps.sales.quotation.serializers import QuotationCommonValidate
from apps.masterdata.saledata.serializers import ProductForSaleListSerializer
from apps.shared import AccountsMsg, ProductMsg, PriceMsg, SaleMsg, HRMsg, PromoMsg, ShippingMsg, \
    DisperseModel, WarehouseMsg
from apps.shared.translations.expense import ExpenseMsg


class SaleOrderCommonCreate:

    @classmethod
    def create_product(cls, validated_data, instance):
        instance.sale_order_product_sale_order.all().delete()
        SaleOrderProduct.objects.bulk_create(
            [SaleOrderProduct(
                sale_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **sale_order_product,
            ) for sale_order_product in validated_data['sale_order_products_data']]
        )
        return True

    @classmethod
    def create_logistic(cls, validated_data, instance):
        old_logistic = SaleOrderLogistic.objects.filter(sale_order=instance)
        if old_logistic:
            old_logistic.delete()
        SaleOrderLogistic.objects.create(
            **validated_data['sale_order_logistic_data'],
            sale_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
        )
        return True

    @classmethod
    def create_cost(cls, validated_data, instance):
        instance.sale_order_cost_sale_order.all().delete()
        SaleOrderCost.objects.bulk_create(
            [SaleOrderCost(
                sale_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **sale_order_cost,
            ) for sale_order_cost in validated_data['sale_order_costs_data']]
        )
        return True

    @classmethod
    def create_expense(cls, validated_data, instance):
        instance.sale_order_expense_sale_order.all().delete()
        SaleOrderExpense.objects.bulk_create(
            [SaleOrderExpense(
                sale_order=instance, tenant_id=instance.tenant_id, company_id=instance.company_id,
                **sale_order_expense,
            ) for sale_order_expense in validated_data['sale_order_expenses_data']]
        )
        return True

    @classmethod
    def create_indicator(cls, validated_data, instance):
        instance.sale_order_indicator_sale_order.all().delete()
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
        instance.payment_stage_sale_order.all().delete()
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
    def create_sale_order_sub_models(cls, validated_data, instance):
        if 'sale_order_products_data' in validated_data:
            cls.create_product(validated_data=validated_data, instance=instance)
        if 'sale_order_logistic_data' in validated_data:
            cls.create_logistic(
                validated_data=validated_data,
                instance=instance
            )
        if 'sale_order_costs_data' in validated_data:
            cls.create_cost(validated_data=validated_data, instance=instance)
        if 'sale_order_expenses_data' in validated_data:
            cls.create_expense(validated_data=validated_data, instance=instance)
        # indicator tab
        if 'sale_order_indicators_data' in validated_data:
            cls.create_indicator(
                validated_data=validated_data,
                instance=instance
            )
        # payment stage tab
        if 'sale_order_payment_stage' in validated_data:
            cls.create_payment_stage(
                validated_data=validated_data,
                instance=instance
            )
        return True


class SaleOrderCommonValidate:

    @classmethod
    def validate_customer_id(cls, value):
        try:
            return Account.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            if value is None:
                return value
            return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': SaleMsg.OPPORTUNITY_NOT_EXIST})

    @classmethod
    def validate_contact_id(cls, value):
        try:
            return Contact.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'contact': AccountsMsg.CONTACT_NOT_EXIST})

    @classmethod
    def validate_payment_term_id(cls, value):
        try:
            if value is None:
                return None
            return PaymentTerm.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except PaymentTerm.DoesNotExist:
            raise serializers.ValidationError({'payment_term': AccountsMsg.PAYMENT_TERM_NOT_EXIST})

    @classmethod
    def validate_quotation_id(cls, value):
        try:
            if value is None:
                return None
            return Quotation.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Quotation.DoesNotExist:
            raise serializers.ValidationError({'quotation': SaleMsg.QUOTATION_NOT_EXIST})

    @classmethod
    def validate_product(cls, value):
        try:
            Product.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': ProductMsg.PRODUCT_DOES_NOT_EXIST})

    @classmethod
    def validate_unit_of_measure(cls, value):
        try:
            UnitOfMeasure.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError({'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST})

    @classmethod
    def validate_tax(cls, value):
        try:
            Tax.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except Tax.DoesNotExist:
            raise serializers.ValidationError({'tax': ProductMsg.TAX_DOES_NOT_EXIST})

    @classmethod
    def validate_expense(cls, value):
        try:
            Expense.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except Expense.DoesNotExist:
            raise serializers.ValidationError({'expense': ProductMsg.EXPENSE_DOES_NOT_EXIST})

    @classmethod
    def validate_expense_item(cls, value):
        try:
            ExpenseItem.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except ExpenseItem.DoesNotExist:
            raise serializers.ValidationError({'expense_item': ExpenseMsg.EXPENSE_ITEM_NOT_EXIST})

    @classmethod
    def validate_price_list(cls, value):
        if isinstance(value, list):
            price_list = Price.objects.filter_current(fill__tenant=True, fill__company=True, id__in=value)
            if price_list.count() == len(value):
                return [
                    {'id': str(price.id), 'title': price.title, 'code': price.code}
                    for price in price_list
                ]
            raise serializers.ValidationError({'price_list': PriceMsg.PRICE_LIST_IS_ARRAY})
        raise serializers.ValidationError({'price_list': PriceMsg.PRICE_LIST_NOT_EXIST})

    @classmethod
    def validate_promotion(cls, value):
        try:
            Promotion.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except Promotion.DoesNotExist:
            raise serializers.ValidationError({'promotion': PromoMsg.PROMOTION_NOT_EXIST})

    @classmethod
    def validate_shipping(cls, value):
        try:
            Shipping.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except Shipping.DoesNotExist:
            raise serializers.ValidationError({'shipping': ShippingMsg.SHIPPING_NOT_EXIST})

    @classmethod
    def validate_indicator(cls, value):
        try:
            indicator = SaleOrderIndicatorConfig.objects.get_current(fill__company=True, id=value)
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
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': HRMsg.EMPLOYEES_NOT_EXIST})

    @classmethod
    def validate_term_id(cls, value):
        try:
            return str(Term.objects.get(id=value).id)
        except Term.DoesNotExist:
            raise serializers.ValidationError({'term': AccountsMsg.PAYMENT_TERM_NOT_EXIST})

    @classmethod
    def validate_warehouse(cls, value):
        try:
            WareHouse.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            return str(value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': WarehouseMsg.WAREHOUSE_NOT_EXIST})


class SaleOrderValueValidate:
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


class SaleOrderRuleValidate:
    @classmethod
    def validate_config_role(cls, validate_data):
        if 'employee_inherit_id' in validate_data:
            opportunity_id = validate_data.get('opportunity_id', None)
            model_cls = DisperseModel(app_model="hr.employee").get_model()
            if model_cls and hasattr(model_cls, 'objects'):
                so_config = QuotationAppConfig.objects.filter_current(fill__tenant=True, fill__company=True).first()
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
    def validate_payment_stage(cls, validate_data):
        if 'sale_order_payment_stage' in validate_data and 'total_product' in validate_data:
            if len(validate_data['sale_order_payment_stage']) > 0:
                total_ratio = 0
                total_payment = 0
                for payment_stage in validate_data['sale_order_payment_stage']:
                    total_ratio += payment_stage.get('payment_ratio', 0)
                    total_payment += payment_stage.get('value_total', 0)
                    # check required field
                    date = payment_stage.get('date', '')
                    due_date = payment_stage.get('due_date', '')
                    if not date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DATE_REQUIRED})
                    if not due_date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DUE_DATE_REQUIRED})
                if total_ratio != 100:
                    raise serializers.ValidationError({'detail': SaleMsg.TOTAL_RATIO_PAYMENT})
                if total_payment != validate_data.get('total_product', 0):
                    raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
            else:
                # check required by config
                so_config = QuotationAppConfig.objects.filter_current(fill__tenant=True, fill__company=True).first()
                if so_config:
                    if so_config.is_require_payment is True:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_REQUIRED_BY_CONFIG})
        return True

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


# SUB SERIALIZERS
class SaleOrderProductSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)
    promotion_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = SaleOrderProduct
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
            'remain_for_purchase_request',
            'remain_for_purchase_order',
            'quantity_wo_remain',
        )

    @classmethod
    def validate_product_id(cls, value):
        return SaleOrderCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)

    @classmethod
    def validate_promotion_id(cls, value):
        return SaleOrderCommonValidate().validate_promotion(value=value)

    @classmethod
    def validate_shipping_id(cls, value):
        return SaleOrderCommonValidate().validate_shipping(value=value)

    @classmethod
    def validate_product_quantity(cls, value):
        return SaleOrderValueValidate.validate_quantity(value=value)

    @classmethod
    def validate_product_unit_price(cls, value):
        return SaleOrderValueValidate.validate_price(value=value)


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
    product_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)
    shipping_id = serializers.UUIDField(required=False, allow_null=True)
    warehouse_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = SaleOrderCost
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
        return SaleOrderCommonValidate().validate_product(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)

    @classmethod
    def validate_shipping_id(cls, value):
        return SaleOrderCommonValidate().validate_shipping(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return SaleOrderCommonValidate().validate_warehouse(value=value)

    @classmethod
    def validate_product_quantity(cls, value):
        return SaleOrderValueValidate.validate_quantity(value=value)


class SaleOrderExpenseSerializer(serializers.ModelSerializer):
    expense_id = serializers.UUIDField(required=False, allow_null=True)
    expense_item_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = SaleOrderExpense
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
            'is_labor',
        )

    @classmethod
    def validate_expense_id(cls, value):
        return SaleOrderCommonValidate().validate_expense(value=value)

    @classmethod
    def validate_expense_item_id(cls, value):
        return SaleOrderCommonValidate().validate_expense_item(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax(value=value)


class SaleOrderIndicatorSerializer(serializers.ModelSerializer):
    quotation_indicator = serializers.UUIDField()

    class Meta:
        model = SaleOrderIndicator
        fields = (
            'quotation_indicator',
            'quotation_indicator_data',
            'indicator_value',
            'indicator_rate',
            'quotation_indicator_value',
            'quotation_indicator_rate',
            'difference_indicator_value',
            'order',
        )

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
            'date_type',
            'payment_ratio',
            'value_before_tax',
            'issue_invoice',
            'value_after_tax',
            'value_total',
            'due_date',
            'is_ar_invoice',
            'order',
        )

    # @classmethod
    # def validate_remark(cls, value):
    #     if not value:
    #         raise serializers.ValidationError({'remark': APIMsg.FIELD_REQUIRED})
    #     return value

    @classmethod
    def validate_term_id(cls, value):
        return SaleOrderCommonValidate().validate_term_id(value=value)
