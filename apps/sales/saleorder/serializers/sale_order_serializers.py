from rest_framework import serializers

from apps.core.process.utils import ProcessRuntimeControl
from apps.core.recurrence.models import Recurrence
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.opportunity.models import Opportunity
from apps.sales.saleorder.serializers.sale_order_sub import SaleOrderCommonCreate, SaleOrderCommonValidate, \
    SaleOrderProductSerializer, SaleOrderLogisticSerializer, SaleOrderCostSerializer, SaleOrderExpenseSerializer, \
    SaleOrderIndicatorSerializer, SaleOrderPaymentStageSerializer, SaleOrderRuleValidate, SaleOrderInvoiceSerializer
from apps.sales.saleorder.models import SaleOrderProduct, SaleOrderExpense, SaleOrder
from apps.shared import SaleMsg, BaseMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel


# SALE ORDER BEGIN
class SaleOrderListSerializer(AbstractListSerializerModel):
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
            'opportunity',
            'quotation',
            'delivery_call',
            'delivery_status',
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
            'is_deal_close': obj.opportunity.is_deal_close,
        } if obj.opportunity else {}

    @classmethod
    def get_quotation(cls, obj):
        return {
            'id': obj.quotation_id,
            'title': obj.quotation.title,
            'code': obj.quotation.code,
            'indicator_revenue': obj.quotation.indicator_revenue,
        } if obj.quotation else {}


class SaleOrderMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'date_created',
        )


class SaleOrderDetailSerializer(AbstractDetailSerializerModel):
    opportunity = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process.id,
                'title': obj.process.title,
                'remark': obj.process.remark,
            }
        return {}

    @classmethod
    def get_process_stage_app(cls, obj):
        if obj.process_stage_app:
            return {
                'id': obj.process_stage_app.id,
                'title': obj.process_stage_app.title,
                'remark': obj.process_stage_app.remark,
            }
        return {}

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'opportunity',
            'customer_data',
            'contact_data',
            'sale_person',
            'payment_term_data',
            'quotation_data',
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
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            # payment stage tab
            'sale_order_payment_stage',
            'sale_order_invoice',
            # system
            'workflow_runtime_id',
            'is_active',
            'employee_inherit',
            # process
            'process',
            'process_stage_app',
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
            } if obj.opportunity.customer else {},
            'is_deal_close': obj.opportunity.is_deal_close,
        } if obj.opportunity else {}

    @classmethod
    def get_sale_person(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}


class SaleOrderCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer_id = serializers.UUIDField()
    contact_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    payment_term_id = serializers.UUIDField(allow_null=True, required=False)
    quotation_id = serializers.UUIDField(
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
    sale_order_invoice = SaleOrderInvoiceSerializer(
        many=True,
        required=False
    )
    # recurrence
    recurrence_task_id = serializers.UUIDField(allow_null=True, required=False)

    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=SaleOrder.get_app_id(),
        ) if attrs else None

    class Meta:
        model = SaleOrder
        fields = (
            # process
            'process',
            'process_stage_app',
            #
            'title',
            'code',
            'opportunity_id',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'employee_inherit_id',
            'payment_term_id',
            'payment_term_data',
            'quotation_id',
            'quotation_data',
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
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            # payment stage tab
            'sale_order_payment_stage',
            'sale_order_invoice',
            # recurrence
            'is_recurrence_template',
            'is_recurring',
            'recurrence_task_id',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return SaleOrderCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return SaleOrderCommonValidate().validate_opportunity_id(value=value)

    @classmethod
    def validate_contact_id(cls, value):
        return SaleOrderCommonValidate().validate_contact_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return SaleOrderCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term_id(cls, value):
        return SaleOrderCommonValidate().validate_payment_term_id(value=value)

    @classmethod
    def validate_quotation_id(cls, value):
        return SaleOrderCommonValidate().validate_quotation_id(value=value)

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
                opportunity = Opportunity.objects.filter(id=validate_data['opportunity_id']).first()
                if opportunity:
                    if opportunity.is_close_lost is True or opportunity.is_deal_close is True:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    is_change = validate_data.get('is_change', False)
                    if is_change is False:
                        if opportunity.sale_order_opportunity.filter(system_status__in=[0, 1, 2, 3]).exists():
                            raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_HAS_SALE_ORDER})
        return True

    def validate(self, validate_data):
        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        opportunity_id = validate_data.get('opportunity_id', None)  # UUID or None
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=opportunity_id)

        SaleOrderRuleValidate.validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        SaleOrderRuleValidate().validate_then_set_indicators_value(validate_data=validate_data)
        SaleOrderRuleValidate.validate_payment_stage(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        sale_order = SaleOrder.objects.create(**validated_data)
        SaleOrderCommonCreate().create_sale_order_sub_models(validated_data=validated_data, instance=sale_order)

        # Check instance is change document => set is_change True for root
        if sale_order.is_change is True and sale_order.document_root_id:
            document_root = SaleOrder.objects.filter_on_company(id=sale_order.document_root_id).first()
            if document_root:
                document_root.is_change = True
                document_root.save(update_fields=['is_change'])

        if sale_order.process:
            ProcessRuntimeControl(process_obj=sale_order.process).register_doc(
                process_stage_app_obj=sale_order.process_stage_app,
                app_id=SaleOrder.get_app_id(),
                doc_id=sale_order.id,
                doc_title=sale_order.title,
                employee_created_id=sale_order.employee_created_id,
                date_created=sale_order.date_created,
            )
        return sale_order


class SaleOrderUpdateSerializer(AbstractCreateSerializerModel):
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    contact_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    employee_inherit_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    payment_term_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    quotation_id = serializers.UUIDField(
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
    sale_order_invoice = SaleOrderInvoiceSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = SaleOrder
        fields = (
            'title',
            'opportunity_id',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'employee_inherit_id',
            'payment_term_id',
            'payment_term_data',
            'quotation_id',
            'quotation_data',
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
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            # payment stage tab
            'sale_order_payment_stage',
            'sale_order_invoice',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return SaleOrderCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return SaleOrderCommonValidate().validate_opportunity_id(value=value)

    @classmethod
    def validate_contact_id(cls, value):
        return SaleOrderCommonValidate().validate_contact_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return SaleOrderCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term_id(cls, value):
        return SaleOrderCommonValidate().validate_payment_term_id(value=value)

    @classmethod
    def validate_quotation_id(cls, value):
        return SaleOrderCommonValidate().validate_quotation_id(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return SaleOrderCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return SaleOrderCommonValidate().validate_customer_billing(value=value)

    def validate_opportunity_rules(self, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_on_company(id=validate_data['opportunity_id']).first()
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
        # update sale order
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        SaleOrderCommonCreate().create_sale_order_sub_models(validated_data=validated_data, instance=instance)
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
        product_data = []
        for item in so_product:
            product_data.append({
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
            })
        return product_data


class SaleOrderPurchasingStaffListSerializer(serializers.ModelSerializer):
    is_create_purchase_request = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

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

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "code": obj.employee_inherit.code,
            "full_name": obj.employee_inherit.get_full_name(2),
            "group": {
                "id": str(obj.employee_inherit.group_id),
                "title": obj.employee_inherit.group.title,
                "code": obj.employee_inherit.group.code
            } if obj.employee_inherit.group_id else {}
        } if obj.employee_inherit else {}


class SOProductWOListSerializer(serializers.ModelSerializer):
    quantity_so = serializers.SerializerMethodField()
    quantity_wo_completed = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrderProduct
        fields = (
            'product_data',
            'uom_data',
            'quantity_so',
            'quantity_wo_completed',
            'quantity_wo_remain',
            'order',
        )

    @classmethod
    def get_quantity_so(cls, obj):
        return obj.product_quantity

    @classmethod
    def get_quantity_wo_completed(cls, obj):
        return obj.product_quantity - obj.quantity_wo_remain


class SORecurrenceListSerializer(AbstractListSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    recurrence_list = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit',
            'date_created',
            'status',
            'recurrence_list',
        )

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}

    @classmethod
    def get_status(cls, obj):
        return Recurrence.objects.filter(doc_template_id=obj.id).exists()

    @classmethod
    def get_recurrence_list(cls, obj):
        return [{
            'id': recurrence.id,
            'title': recurrence.title,
        } for recurrence in Recurrence.objects.filter(doc_template_id=obj.id)]
