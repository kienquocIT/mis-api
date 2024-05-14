from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.opportunity.models import Opportunity, OpportunityActivityLogs
from apps.sales.saleorder.serializers.sale_order_sub import SaleOrderCommonCreate, SaleOrderCommonValidate, \
    SaleOrderProductSerializer, SaleOrderLogisticSerializer, SaleOrderCostSerializer, SaleOrderExpenseSerializer, \
    SaleOrderIndicatorSerializer, SaleOrderPaymentStageSerializer, SaleOrderRuleValidate
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderExpense, SaleOrder
from apps.shared import SaleMsg, BaseMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel


# SALE ORDER BEGIN
class SaleOrderListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
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
            'indicator_revenue',
            'system_status',
            'opportunity',
            'quotation',
            'delivery_call',
            'delivery_status',
            'is_change',
            'document_change_order',
            'document_root_id',
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_quotation(cls, obj):
        return {
            'id': obj.quotation_id,
            'title': obj.quotation.title,
            'code': obj.quotation.code,
        } if obj.quotation else {}


class SaleOrderDetailSerializer(AbstractDetailSerializerModel):
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

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
            'payment_term_id',
            'payment_term_data',
            'quotation',
            'system_status',
            # sale order tabs
            'sale_order_products_data',
            'sale_order_logistic_data',
            'customer_shipping_id',
            'customer_billing_id',
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
            # payment stage tab
            'sale_order_payment_stage',
            # system
            'workflow_runtime_id',
            'is_active',
            'employee_inherit',
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'customer': {
                'id': obj.opportunity.customer_id,
                'title': obj.opportunity.customer.title
            } if obj.opportunity.customer else {}
        } if obj.opportunity else {}

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
            'payment_term_mapped': {
                'id': obj.customer.payment_term_customer_mapped_id,
                'title': obj.customer.payment_term_customer_mapped.title,
                'code': obj.customer.payment_term_customer_mapped.code,
            } if obj.customer.payment_term_customer_mapped else {}
        } if obj.customer else {}

    @classmethod
    def get_contact(cls, obj):
        return {
            'id': obj.contact_id,
            'title': obj.contact.fullname,
            'code': obj.contact.code,
        } if obj.contact else {}

    @classmethod
    def get_sale_person(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'phone': obj.employee_inherit.phone,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}

    @classmethod
    def get_quotation(cls, obj):
        return {
            'id': obj.quotation_id,
            'title': obj.quotation.title,
            'code': obj.quotation.code,
            'quotation_indicators_data': obj.quotation.quotation_indicators_data,
        } if obj.quotation else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'phone': obj.employee_inherit.phone,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}


class SaleOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField()
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer = serializers.UUIDField()
    contact = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    payment_term = serializers.UUIDField()
    quotation = serializers.UUIDField(
        allow_null=True,
        required=False
    )
    # sale order tabs
    sale_order_products_data = SaleOrderProductSerializer(
        many=True,
        required=False
    )
    sale_order_logistic_data = SaleOrderLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
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
    # payment stage tab
    sale_order_payment_stage = SaleOrderPaymentStageSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = SaleOrder
        fields = (
            'title',
            'code',
            'opportunity_id',
            'customer',
            'contact',
            'employee_inherit_id',
            'payment_term',
            'payment_term_data',
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
            'customer_shipping',
            'customer_billing',
            'sale_order_costs_data',
            'sale_order_expenses_data',
            # indicator tab
            'sale_order_indicators_data',
            # payment stage tab
            'sale_order_payment_stage',
            # system
            'system_status',
        )

    @classmethod
    def validate_customer(cls, value):
        return SaleOrderCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return SaleOrderCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return SaleOrderCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return SaleOrderCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return SaleOrderCommonValidate().validate_payment_term(value=value)

    @classmethod
    def validate_quotation(cls, value):
        return SaleOrderCommonValidate().validate_quotation(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return SaleOrderCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return SaleOrderCommonValidate().validate_customer_billing(value=value)

    @classmethod
    def validate_opportunity_rules(cls, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=validate_data['opportunity_id']
                ).first()
                if opportunity:
                    if opportunity.is_close_lost is True or opportunity.is_deal_close is True:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    if opportunity.sale_order_opportunity.filter(system_status__in=[0, 1, 2, 3]).exists():
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_HAS_SALE_ORDER})
        return True

    def validate(self, validate_data):
        SaleOrderRuleValidate.validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        SaleOrderRuleValidate().validate_then_set_indicators_value(validate_data=validate_data)
        SaleOrderRuleValidate.validate_payment_stage(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        sale_order = SaleOrder.objects.create(**validated_data)
        SaleOrderCommonCreate().create_sale_order_sub_models(
            validated_data=validated_data,
            instance=sale_order
        )
        # update field sale_order & create activity log for opportunity
        if sale_order.opportunity:
            # update field sale_order
            sale_order.opportunity.sale_order = sale_order
            sale_order.opportunity.save(update_fields=['sale_order'])
            # create activity log
            OpportunityActivityLogs.create_opportunity_log_application(
                tenant_id=sale_order.tenant_id,
                company_id=sale_order.company_id,
                opportunity_id=sale_order.opportunity_id,
                employee_created_id=sale_order.employee_created_id,
                app_code=str(sale_order.__class__.get_model_code()),
                doc_id=sale_order.id,
                title=sale_order.title,
            )
        return sale_order


class SaleOrderUpdateSerializer(serializers.ModelSerializer):
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    contact = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    employee_inherit_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    payment_term = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    quotation = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    # sale order tabs
    sale_order_products_data = SaleOrderProductSerializer(
        many=True,
        required=False
    )
    sale_order_logistic_data = SaleOrderLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
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
    # payment stage tab
    sale_order_payment_stage = SaleOrderPaymentStageSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = SaleOrder
        fields = (
            'title',
            'opportunity_id',
            'customer',
            'contact',
            'employee_inherit_id',
            'payment_term',
            'payment_term_data',
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
            'customer_shipping',
            'customer_billing',
            'sale_order_costs_data',
            'sale_order_expenses_data',
            # indicator tab
            'sale_order_indicators_data',
            # payment stage tab
            'sale_order_payment_stage',
            # status
            'system_status',
        )

    @classmethod
    def validate_customer(cls, value):
        return SaleOrderCommonValidate().validate_customer(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return SaleOrderCommonValidate().validate_opportunity(value=value)

    @classmethod
    def validate_contact(cls, value):
        return SaleOrderCommonValidate().validate_contact(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return SaleOrderCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return SaleOrderCommonValidate().validate_payment_term(value=value)

    @classmethod
    def validate_quotation(cls, value):
        return SaleOrderCommonValidate().validate_quotation(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return SaleOrderCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return SaleOrderCommonValidate().validate_customer_billing(value=value)

    def validate_opportunity_rules(self, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=validate_data['opportunity_id']
                ).first()
                if opportunity:
                    if opportunity.is_close_lost is True or opportunity.is_deal_close is True:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    if opportunity.sale_order_opportunity.filter(
                            system_status__in=[0, 1, 2, 3]
                    ).exclude(id=self.instance.id).exists():
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_SALE_ORDER_USED})
        return True

    def validate_system_status(self, attrs):
        if attrs in [0, 1]:  # draft or created
            if self.instance.system_status <= attrs:
                return attrs
        raise serializers.ValidationError({
            'system_status': BaseMsg.SYSTEM_STATUS_INCORRECT,
        })

    def validate(self, validate_data):
        SaleOrderRuleValidate.validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        SaleOrderRuleValidate().validate_then_set_indicators_value(validate_data=validate_data)
        SaleOrderRuleValidate.validate_payment_stage(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        # check if change opportunity then update field sale_order in opportunity to None
        if instance.opportunity_id != validated_data.get('opportunity_id', None):
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
            instance.opportunity.save(update_fields=['sale_order'])
        return instance


class SaleOrderExpenseListSerializer(serializers.ModelSerializer):
    tax = serializers.SerializerMethodField()
    plan_after_tax = serializers.SerializerMethodField()
    expense_item = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrderExpense
        fields = (
            'id',
            'expense_title',
            'expense_item',
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

    @classmethod
    def get_expense_item(cls, obj):
        if obj.expense_item:
            return {'id': obj.expense_item_id, 'code': obj.expense_item.code, 'title': obj.expense_item.title}
        return {}


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
        so_product = SaleOrderProduct.objects.select_related(
            'product__purchase_default_uom',
            'product__purchase_tax',
            'product__general_uom_group',
            'unit_of_measure',
            'tax'
        ).filter(
            sale_order=obj,
            product__isnull=False
        )
        return [
            {
                'id': item.id,
                'product_quantity': item.product_quantity,
                'remain_for_purchase_request': item.remain_for_purchase_request,
                'product': {
                    'id': item.product_id,
                    'title': item.product.title,
                    'code': item.product.code,
                    'description': item.product.description,
                    'product_choice': item.product.product_choice,
                    'uom': {
                        'id': item.product.purchase_default_uom_id,
                        'title': item.product.purchase_default_uom.title if item.product.purchase_default_uom else ''
                    } if item.product.purchase_default_uom else {},
                    'uom_group': item.product.general_uom_group.title if item.product.general_uom_group else ''
                } if item.product else {},
                'uom': {
                    'id': item.unit_of_measure_id,
                    'title': item.unit_of_measure.title,
                    'code': item.unit_of_measure.code,
                    'ratio': item.unit_of_measure.ratio
                } if item.unit_of_measure else {},
                'tax': {
                    'id': item.tax_id,
                    'title': item.tax.title,
                    'rate': item.tax.rate
                } if item.tax else {},
            }
            for item in so_product
        ]


class SaleOrderPurchasingStaffListSerializer(serializers.ModelSerializer):
    is_create_purchase_request = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'code',
            'title',
            'employee_inherit',
            'is_create_purchase_request',
        )

    @classmethod
    def get_is_create_purchase_request(cls, obj):
        so_product = obj.sale_order_product_sale_order.all()
        return any(item.remain_for_purchase_request > 0 and item.product_id is not None for item in so_product)
