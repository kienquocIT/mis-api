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
    SaleOrderIndicatorConfig, SaleOrderIndicator, SaleOrderPaymentStage, SaleOrderInvoice
from apps.sales.quotation.serializers import QuotationCommonValidate
from apps.masterdata.saledata.serializers import ProductForSaleListSerializer
from apps.shared import PriceMsg, SaleMsg, DisperseModel, BaseMsg


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
        instance.sale_order_payment_stage_sale_order.all().delete()
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
    def create_invoice(cls, validated_data, instance):
        instance.sale_order_invoice_sale_order.all().delete()
        SaleOrderInvoice.objects.bulk_create(
            [SaleOrderInvoice(
                sale_order=instance,
                tenant_id=instance.tenant_id,
                company_id=instance.company_id,
                **sale_order_invoice,
            ) for sale_order_invoice in validated_data['sale_order_invoice']]
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
        if 'sale_order_invoice' in validated_data:
            cls.create_invoice(
                validated_data=validated_data,
                instance=instance
            )
        return True


class SaleOrderCommonValidate:

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
    def validate_quotation_id(cls, value):
        try:
            if value is None:
                return None
            return str(Quotation.objects.get_on_company(id=value).id)
        except Quotation.DoesNotExist:
            raise serializers.ValidationError({'quotation': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_product_id(cls, value):
        try:
            return str(Product.objects.get_on_company(id=value).id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        try:
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
            indicator = SaleOrderIndicatorConfig.objects.get_on_company(id=value)
            return {
                'id': str(indicator.id),
                'title': indicator.title,
                'remark': indicator.remark
            }
        except SaleOrderIndicatorConfig.DoesNotExist:
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
    def validate_term_id(cls, value):
        try:
            return str(Term.objects.get(id=value).id)
        except Term.DoesNotExist:
            raise serializers.ValidationError({'term': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_warehouse(cls, value):
        try:
            WareHouse.objects.get_on_company(id=value)
            return str(value)
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse': BaseMsg.NOT_EXIST})


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
    def validate_payment_stage(cls, validate_data):
        if 'sale_order_payment_stage' in validate_data and 'total_product' in validate_data:
            if len(validate_data['sale_order_payment_stage']) > 0:
                total_payment = 0
                for payment_stage in validate_data['sale_order_payment_stage']:
                    total_payment += payment_stage.get('value_total', 0)
                    # check required field
                    date = payment_stage.get('date', '')
                    due_date = payment_stage.get('due_date', '')
                    if not date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DATE_REQUIRED})
                    if not due_date:
                        raise serializers.ValidationError({'detail': SaleMsg.PAYMENT_DUE_DATE_REQUIRED})
                if total_payment != validate_data.get('total_product', 0):
                    raise serializers.ValidationError({'detail': SaleMsg.TOTAL_PAYMENT})
            else:
                # check required by config
                so_config = QuotationAppConfig.objects.filter_on_company().first()
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
    unit_of_measure_id = serializers.UUIDField(error_messages={
        'required': SaleMsg.PRODUCT_UOM_REQUIRED,
    })
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
        return SaleOrderCommonValidate().validate_product_id(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax_id(value=value)

    @classmethod
    def validate_promotion_id(cls, value):
        return SaleOrderCommonValidate().validate_promotion_id(value=value)

    @classmethod
    def validate_shipping_id(cls, value):
        return SaleOrderCommonValidate().validate_shipping_id(value=value)

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
        return SaleOrderCommonValidate().validate_product_id(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax_id(value=value)

    @classmethod
    def validate_shipping_id(cls, value):
        return SaleOrderCommonValidate().validate_shipping_id(value=value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return SaleOrderCommonValidate().validate_warehouse(value=value)

    # @classmethod
    # def validate_product_quantity(cls, value):
    #     return SaleOrderValueValidate.validate_quantity(value=value)


class SaleOrderExpenseSerializer(serializers.ModelSerializer):
    expense_id = serializers.UUIDField(required=False, allow_null=True)
    expense_item_id = serializers.UUIDField(required=False, allow_null=True)
    unit_of_measure_id = serializers.UUIDField(error_messages={
        'required': SaleMsg.EXPENSE_UOM_REQUIRED,
    })
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
        return SaleOrderCommonValidate().validate_expense_id(value=value)

    @classmethod
    def validate_expense_item_id(cls, value):
        return SaleOrderCommonValidate().validate_expense_item_id(value=value)

    @classmethod
    def validate_unit_of_measure_id(cls, value):
        return SaleOrderCommonValidate().validate_unit_of_measure_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax_id(value=value)


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
    tax_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = SaleOrderPaymentStage
        fields = (
            'remark',
            'term_id',
            'term_data',
            'date',
            'due_date',
            'ratio',
            'invoice',
            'invoice_data',
            'value_before_tax',
            'value_reconcile',
            'reconcile_data',
            'tax_id',
            'tax_data',
            'value_tax',
            'value_total',
            'is_ar_invoice',
            'order',
        )

    @classmethod
    def validate_term_id(cls, value):
        return SaleOrderCommonValidate().validate_term_id(value=value)

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax_id(value=value)


class SaleOrderInvoiceSerializer(serializers.ModelSerializer):
    date = serializers.CharField(required=False, allow_null=True)
    tax_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = SaleOrderInvoice
        fields = (
            'remark',
            'date',
            'term_data',
            'ratio',
            'tax_id',
            'tax_data',
            'total',
            'balance',
            'order',
        )

    @classmethod
    def validate_tax_id(cls, value):
        return SaleOrderCommonValidate().validate_tax_id(value=value)
