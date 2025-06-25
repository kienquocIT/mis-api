from rest_framework import serializers

from apps.core.base.models import Application
from apps.core.process.utils import ProcessRuntimeControl
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation, QuotationExpense, QuotationAttachment
from apps.sales.quotation.serializers.quotation_sub import QuotationCommonCreate, QuotationCommonValidate, \
    QuotationProductSerializer, QuotationLogisticSerializer, QuotationCostSerializer, \
    QuotationExpenseSerializer, QuotationIndicatorSerializer, QuotationRuleValidate
from apps.shared import SaleMsg, BaseMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel, SerializerCommonValidate, SerializerCommonHandle, \
    AbstractCurrencyCreateSerializerModel, AbstractCurrencyDetailSerializerModel


# QUOTATION BEGIN
class QuotationListSerializer(AbstractListSerializerModel):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
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
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': str(obj.customer_id),
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': str(obj.opportunity_id),
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}


class QuotationMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code',
            'date_created',
        )


class QuotationDetailSerializer(AbstractDetailSerializerModel, AbstractCurrencyDetailSerializerModel):
    opportunity = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code',
            'opportunity',
            'customer_data',
            'contact_data',
            'sale_person',
            'payment_term_data',
            'system_status',
            # quotation tabs
            'quotation_products_data',
            'quotation_logistic_data',
            'customer_shipping_id',
            'customer_billing_id',
            'quotation_costs_data',
            'quotation_expenses_data',
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
            'is_customer_confirm',
            'date_created',
            # indicator tab
            'quotation_indicators_data',
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
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
            'id': str(obj.opportunity_id),
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'is_close_lost': obj.opportunity.is_close_lost,
            'is_deal_close': obj.opportunity.is_deal_close,
            'sale_order_id': str(obj.opportunity.sale_order_id),
            'customer': {
                'id': str(obj.opportunity.customer_id),
                'title': obj.opportunity.customer.title
            } if obj.opportunity.customer else {},
            'quotation_id': str(obj.opportunity.quotation_id),
        } if obj.opportunity else {}

    @classmethod
    def get_sale_person(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return obj.employee_inherit.get_detail_minimal() if obj.employee_inherit else {}

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

    @classmethod
    def get_attachment(cls, obj):
        return [file_obj.get_detail() for file_obj in obj.attachment_m2m.all()]


class QuotationCreateSerializer(AbstractCreateSerializerModel, AbstractCurrencyCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    opportunity_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )
    customer_id = serializers.UUIDField()
    contact_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    payment_term_id = serializers.UUIDField(allow_null=True, required=False)
    # quotation tabs
    quotation_products_data = QuotationProductSerializer(
        many=True,
        required=False
    )
    quotation_logistic_data = QuotationLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
    quotation_costs_data = QuotationCostSerializer(
        many=True,
        required=False
    )
    quotation_expenses_data = QuotationExpenseSerializer(
        many=True,
        required=False
    )
    # indicator tab
    quotation_indicators_data = QuotationIndicatorSerializer(
        many=True,
        required=False
    )
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=Quotation.get_app_id()
        ) if attrs else None

    class Meta:
        model = Quotation
        fields = (
            # process
            'process',
            'process_stage_app',
            #
            'title',
            'opportunity_id',
            'customer_id',
            'customer_data',
            'contact_id',
            'contact_data',
            'employee_inherit_id',
            'payment_term_id',
            'payment_term_data',
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
            # quotation tabs
            'quotation_products_data',
            'quotation_logistic_data',
            'customer_shipping',
            'customer_billing',
            'quotation_costs_data',
            'quotation_expenses_data',
            'is_customer_confirm',
            # indicator tab
            'quotation_indicators_data',
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            'attachment',
        )

    @classmethod
    def validate_customer_id(cls, value):
        return QuotationCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return QuotationCommonValidate().validate_opportunity_id(value=value)

    @classmethod
    def validate_contact_id(cls, value):
        return QuotationCommonValidate().validate_contact_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return QuotationCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term_id(cls, value):
        return QuotationCommonValidate().validate_payment_term_id(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return QuotationCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return QuotationCommonValidate().validate_customer_billing(value=value)

    @classmethod
    def validate_next_node_collab_id(cls, value):
        return QuotationCommonValidate().validate_next_node_collab_id(value=value)

    @classmethod
    def validate_opportunity_rules(cls, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_on_company(id=validate_data['opportunity_id']).first()
                if opportunity:
                    if opportunity.is_close_lost is True or opportunity.is_deal_close is True:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    if opportunity.sale_order_opportunity.filter(system_status__in=[0, 1, 2, 3]).exists():
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_HAS_SALE_ORDER})
                    is_change = validate_data.get('is_change', False)
                    if is_change is False:
                        if opportunity.quotation_opportunity.filter(system_status__in=[0, 1, 2, 3]).exists():
                            raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_HAS_QUOTATION_NOT_DONE})
        return True

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        return SerializerCommonValidate.validate_attachment(user=user, model_cls=QuotationAttachment, value=value)

    def validate(self, validate_data):
        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        opportunity_id = validate_data.get('opportunity_id', None)
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=opportunity_id)
        QuotationRuleValidate().validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        QuotationRuleValidate().validate_then_set_indicators_value(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        quotation = Quotation.objects.create(**validated_data)
        QuotationCommonCreate().create_quotation_sub_models(validated_data=validated_data, instance=quotation)
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="b9650500-aba7-44e3-b6e0-2542622702a3").first(),
            model_cls=QuotationAttachment,
            instance=quotation,
            attachment_result=attachment,
        )

        # Check instance is change document => set is_change True for root
        if quotation.is_change is True and quotation.document_root_id:
            document_root = Quotation.objects.filter_on_company(id=quotation.document_root_id).first()
            if document_root:
                document_root.is_change = True
                document_root.save(update_fields=['is_change'])

        if quotation.process:
            ProcessRuntimeControl(process_obj=quotation.process).register_doc(
                process_stage_app_obj=quotation.process_stage_app,
                app_id=Quotation.get_app_id(),
                doc_id=quotation.id,
                doc_title=quotation.title,
                employee_created_id=quotation.employee_created_id,
                date_created=quotation.date_created,
            )
        return quotation


class QuotationUpdateSerializer(AbstractCreateSerializerModel):
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
    # quotation tabs
    quotation_products_data = QuotationProductSerializer(
        many=True,
        required=False
    )
    quotation_logistic_data = QuotationLogisticSerializer(required=False)
    customer_shipping = serializers.UUIDField(required=False, allow_null=True)
    customer_billing = serializers.UUIDField(required=False, allow_null=True)
    quotation_costs_data = QuotationCostSerializer(
        many=True,
        required=False
    )
    quotation_expenses_data = QuotationExpenseSerializer(
        many=True,
        required=False
    )
    # indicator tab
    quotation_indicators_data = QuotationIndicatorSerializer(
        many=True,
        required=False
    )
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = Quotation
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
            # quotation tabs
            'quotation_products_data',
            'quotation_logistic_data',
            'customer_shipping',
            'customer_billing',
            'quotation_costs_data',
            'quotation_expenses_data',
            'is_customer_confirm',
            # indicator tab
            'quotation_indicators_data',
            # indicators
            'indicator_revenue',
            'indicator_gross_profit',
            'indicator_net_income',
            'attachment',
        )

    @classmethod
    def validate_customer(cls, value):
        return QuotationCommonValidate().validate_customer_id(value=value)

    @classmethod
    def validate_opportunity_id(cls, value):
        return QuotationCommonValidate().validate_opportunity_id(value=value)

    @classmethod
    def validate_contact(cls, value):
        return QuotationCommonValidate().validate_contact_id(value=value)

    @classmethod
    def validate_employee_inherit_id(cls, value):
        return QuotationCommonValidate().validate_employee_inherit_id(value=value)

    @classmethod
    def validate_payment_term(cls, value):
        return QuotationCommonValidate().validate_payment_term_id(value=value)

    @classmethod
    def validate_customer_shipping(cls, value):
        return QuotationCommonValidate().validate_customer_shipping(value=value)

    @classmethod
    def validate_customer_billing(cls, value):
        return QuotationCommonValidate().validate_customer_billing(value=value)

    def validate_opportunity_rules(self, validate_data):
        if 'opportunity_id' in validate_data:
            if validate_data['opportunity_id'] is not None:
                opportunity = Opportunity.objects.filter_on_company(id=validate_data['opportunity_id']).first()
                if opportunity:
                    if opportunity.is_close_lost is True or opportunity.is_deal_close is True:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    if opportunity.quotation_opportunity.filter(
                            system_status__in=[0, 1, 2, 3]
                    ).exclude(id=self.instance.id).exists():
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_QUOTATION_USED})
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
            user=user, model_cls=QuotationAttachment, value=value, doc_id=self.instance.id
        )

    def validate(self, validate_data):
        QuotationRuleValidate().validate_config_role(validate_data=validate_data)
        self.validate_opportunity_rules(validate_data=validate_data)
        QuotationRuleValidate().validate_then_set_indicators_value(validate_data=validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        # update quotation
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        QuotationCommonCreate().create_quotation_sub_models(validated_data=validated_data, instance=instance)
        SerializerCommonHandle.handle_attach_file(
            relate_app=Application.objects.filter(id="b9650500-aba7-44e3-b6e0-2542622702a3").first(),
            model_cls=QuotationAttachment,
            instance=instance,
            attachment_result=attachment,
        )
        return instance


class QuotationExpenseListSerializer(serializers.ModelSerializer):
    tax = serializers.SerializerMethodField()
    plan_after_tax = serializers.SerializerMethodField()
    expense_item = serializers.SerializerMethodField()

    class Meta:
        model = QuotationExpense
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
