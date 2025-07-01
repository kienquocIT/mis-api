from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.process.utils import ProcessRuntimeControl
from apps.core.recurrence.models import Recurrence
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.opportunity.models import Opportunity
from apps.sales.leaseorder.serializers.lease_order_sub import LeaseOrderCommonCreate, LeaseOrderCommonValidate, \
    LeaseOrderProductSerializer, LeaseOrderCostSerializer, LeaseOrderExpenseSerializer, LeaseOrderIndicatorSerializer, \
    LeaseOrderPaymentStageSerializer, LeaseOrderRuleValidate, LeaseOrderLogisticSerializer, LeaseOrderInvoiceSerializer
from apps.sales.leaseorder.models import LeaseOrder, LeaseOrderAttachment
from apps.shared import SaleMsg, BaseMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel, SerializerCommonValidate, SerializerCommonHandle


# LEASE ORDER BEGIN
class LeaseOrderListSerializer(AbstractListSerializerModel):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    quotation = serializers.SerializerMethodField()

    class Meta:
        model = LeaseOrder
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
            'lease_from',
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
        } if obj.quotation else {}


class LeaseOrderMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseOrder
        fields = (
            'id',
            'title',
            'code',
            'date_created',
        )


class LeaseOrderDetailSerializer(AbstractDetailSerializerModel):
    opportunity = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

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
        model = LeaseOrder
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
            'lease_from',
            'lease_to',
            'system_status',
            # sale order tabs
            'lease_products_data',
            'lease_logistic_data',
            'customer_shipping_id',
            'customer_billing_id',
            'lease_costs_data',
            'lease_costs_leased_data',
            'lease_expenses_data',
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
            'lease_indicators_data',
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            # payment stage tab
            'lease_payment_stage',
            'lease_invoice',
            # system
            'workflow_runtime_id',
            'is_active',
            'employee_inherit',
            # process
            'process',
            'process_stage_app',

            'attachment',
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

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]


class LeaseOrderCreateSerializer(AbstractCreateSerializerModel):
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
    lease_products_data = LeaseOrderProductSerializer(
        many=True,
        required=False
    )
    lease_logistic_data = LeaseOrderLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
    lease_costs_data = LeaseOrderCostSerializer(
        many=True,
        required=False
    )
    lease_expenses_data = LeaseOrderExpenseSerializer(
        many=True,
        required=False
    )
    # indicator tab
    lease_indicators_data = LeaseOrderIndicatorSerializer(
        many=True,
        required=False
    )
    # payment stage tab
    lease_payment_stage = LeaseOrderPaymentStageSerializer(
        many=True,
        required=False
    )
    lease_invoice = LeaseOrderInvoiceSerializer(
        many=True,
        required=False
    )
    # recurrence
    recurrence_task_id = serializers.UUIDField(allow_null=True, required=False)

    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=LeaseOrder.get_app_id(),
        ) if attrs else None

    class Meta:
        model = LeaseOrder
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
            'lease_from',
            'lease_to',
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
            'lease_products_data',
            'lease_logistic_data',
            'customer_shipping',
            'customer_billing',
            'lease_costs_data',
            'lease_expenses_data',
            # indicator tab
            'lease_indicators_data',
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            # payment stage tab
            'lease_payment_stage',
            'lease_invoice',
            # recurrence
            'is_recurrence_template',
            'is_recurring',
            'recurrence_task_id',
            'attachment',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return LeaseOrderCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return LeaseOrderCommonValidate().validate_opportunity_id(value=value)

    @classmethod
    def validate_contact_id(cls, value):
        return LeaseOrderCommonValidate().validate_contact_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return LeaseOrderCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term_id(cls, value):
        return LeaseOrderCommonValidate().validate_payment_term_id(value=value)

    @classmethod
    def validate_quotation_id(cls, value):
        return LeaseOrderCommonValidate().validate_quotation_id(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return LeaseOrderCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return LeaseOrderCommonValidate().validate_customer_billing(value=value)

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
                        if opportunity.lease_opportunity.filter(system_status__in=[0, 1, 2, 3]).exists():
                            raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_HAS_SALE_ORDER})
        return True

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(user=user, model_cls=LeaseOrderAttachment, value=value)

    def validate(self, validate_data):
        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        opportunity_id = validate_data.get('opportunity_id', None)  # UUID or None
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=opportunity_id)

        LeaseOrderRuleValidate.validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        LeaseOrderRuleValidate.validate_then_set_indicators_value(validate_data=validate_data)
        LeaseOrderRuleValidate.validate_payment_stage(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        lease = LeaseOrder.objects.create(**validated_data)
        LeaseOrderCommonCreate().create_lease_sub_models(validated_data=validated_data, instance=lease)
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="010404b3-bb91-4b24-9538-075f5f00ef14").first(),
            model_cls=LeaseOrderAttachment,
            instance=lease,
            attachment_result=attachment,
        )

        if lease.process:
            ProcessRuntimeControl(process_obj=lease.process).register_doc(
                process_stage_app_obj=lease.process_stage_app,
                app_id=LeaseOrder.get_app_id(),
                doc_id=lease.id,
                doc_title=lease.title,
                employee_created_id=lease.employee_created_id,
                date_created=lease.date_created,
            )
        return lease


class LeaseOrderUpdateSerializer(AbstractCreateSerializerModel):
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
    lease_products_data = LeaseOrderProductSerializer(
        many=True,
        required=False
    )
    lease_logistic_data = LeaseOrderLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
    lease_costs_data = LeaseOrderCostSerializer(
        many=True,
        required=False
    )
    lease_expenses_data = LeaseOrderExpenseSerializer(
        many=True,
        required=False
    )
    # indicator tab
    lease_indicators_data = LeaseOrderIndicatorSerializer(
        many=True,
        required=False
    )
    # payment stage tab
    lease_payment_stage = LeaseOrderPaymentStageSerializer(
        many=True,
        required=False
    )
    lease_invoice = LeaseOrderInvoiceSerializer(
        many=True,
        required=False
    )
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = LeaseOrder
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
            'lease_from',
            'lease_to',
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
            'lease_products_data',
            'lease_logistic_data',
            'customer_shipping',
            'customer_billing',
            'lease_costs_data',
            'lease_expenses_data',
            # indicator tab
            'lease_indicators_data',
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            # payment stage tab
            'lease_payment_stage',
            'lease_invoice',
            'attachment',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return LeaseOrderCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return LeaseOrderCommonValidate().validate_opportunity_id(value=value)

    @classmethod
    def validate_contact_id(cls, value):
        return LeaseOrderCommonValidate().validate_contact_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return LeaseOrderCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term_id(cls, value):
        return LeaseOrderCommonValidate().validate_payment_term_id(value=value)

    @classmethod
    def validate_quotation_id(cls, value):
        return LeaseOrderCommonValidate().validate_quotation_id(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return LeaseOrderCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return LeaseOrderCommonValidate().validate_customer_billing(value=value)

    def validate_opportunity_rules(self, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_on_company(id=validate_data['opportunity_id']).first()
                if opportunity:
                    if opportunity.is_close_lost is True or opportunity.is_deal_close is True:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    if opportunity.lease_opportunity.filter(
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

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(
            user=user, model_cls=LeaseOrderAttachment, value=value, doc_id=self.instance.id
        )

    def validate(self, validate_data):
        LeaseOrderRuleValidate.validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        LeaseOrderRuleValidate.validate_then_set_indicators_value(validate_data=validate_data)
        LeaseOrderRuleValidate.validate_payment_stage(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        # update sale order
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        LeaseOrderCommonCreate().create_lease_sub_models(validated_data=validated_data, instance=instance)
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="010404b3-bb91-4b24-9538-075f5f00ef14").first(),
            model_cls=LeaseOrderAttachment,
            instance=instance,
            attachment_result=attachment,
        )
        return instance


class LORecurrenceListSerializer(AbstractListSerializerModel):
    employee_inherit = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    recurrence_list = serializers.SerializerMethodField()

    class Meta:
        model = LeaseOrder
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
