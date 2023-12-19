from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import (
    Payment, PaymentCost, PaymentConfig,
    AdvancePaymentCost
)
from apps.masterdata.saledata.models import Currency, Account
from apps.sales.opportunity.models import OpportunityActivityLogs
from apps.shared import AdvancePaymentMsg, HRMsg, AbstractDetailSerializerModel, SaleMsg


class PaymentListSerializer(serializers.ModelSerializer):
    converted_value_list = serializers.SerializerMethodField()
    return_value_list = serializers.SerializerMethodField()
    payment_value = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'id',
            'code',
            'title',
            'sale_code_type',
            'supplier',
            'method',
            'creator_name',
            'employee_inherit',
            'converted_value_list',
            'return_value_list',
            'payment_value',
            'date_created'
        )

    @classmethod
    def get_converted_value_list(cls, obj):
        all_items = obj.payment.all()
        sum_payment_value = sum(item.expense_after_tax_price for item in all_items)
        return sum_payment_value

    @classmethod
    def get_return_value_list(cls, obj):
        obj.return_value_list = {}
        return obj.return_value_list

    @classmethod
    def get_payment_value(cls, obj):
        all_items = obj.payment.all()
        sum_payment_value = sum(item.expense_after_tax_price for item in all_items)
        return sum_payment_value


def update_ap_cost(payment_cost_list):
    for item in payment_cost_list:
        for child in item.ap_cost_converted_list:
            ap_item_id = child.get('ap_cost_converted_id', None)
            ap_item_value_converted = child.get('value_converted', None)
            if ap_item_id and ap_item_value_converted and item.real_value:
                ap_item = AdvancePaymentCost.objects.filter(id=ap_item_id).first()
                if ap_item:
                    ap_item.sum_converted_value = float(ap_item.sum_converted_value) + float(ap_item_value_converted)
                    ap_item.save()
    return True


def create_payment_cost_items(payment_obj, payment_expense_valid_list):
    vnd_currency = Currency.objects.filter_current(fill__tenant=True, fill__company=True, abbreviation='VND').first()
    if vnd_currency:
        bulk_info = []
        for item in payment_expense_valid_list:
            if float(item['real_value']) + float(item['converted_value']) == float(item['sum_value']):
                bulk_info.append(
                    PaymentCost(
                        **item,
                        payment=payment_obj,
                        currency=vnd_currency,
                        sale_order_mapped=payment_obj.sale_order_mapped,
                        quotation_mapped=payment_obj.quotation_mapped,
                        opportunity_mapped=payment_obj.opportunity_mapped
                    )
                )
            else:
                raise serializers.ValidationError({'Row error': AdvancePaymentMsg.ROW_ERROR})

        PaymentCost.objects.filter(payment=payment_obj).delete()
        payment_cost_list = PaymentCost.objects.bulk_create(bulk_info)
        update_ap_cost(payment_cost_list)
        return True
    return False


class PaymentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Payment
        fields = (
            'title',
            'sale_code_type',
            'supplier',
            'employee_payment',
            'is_internal_payment',
            'method',
            'creator_name',
            'employee_inherit',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped',
            # system
            'system_status',
        )

    @classmethod
    def validate_sale_code_type(cls, attrs):
        if attrs in [0, 1, 2, 3]:
            return attrs
        raise serializers.ValidationError({'Sale code type': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError({'Method': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    def validate(self, validate_data):
        if validate_data.get('opportunity_mapped', None):
            if validate_data['opportunity_mapped'].is_close_lost or validate_data['opportunity_mapped'].is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})

        if validate_data.get('is_internal_payment'):
            if 'supplier' in validate_data:
                validate_data.pop('supplier')
        else:
            if 'employee_payment' in validate_data:
                validate_data.pop('employee_payment')
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        payment_obj = Payment.objects.create(**validated_data)
        if Payment.objects.filter_current(fill__tenant=True, fill__company=True, code=payment_obj.code).count() > 1:
            raise serializers.ValidationError({'detail': HRMsg.INVALID_SCHEMA})
        create_payment_cost_items(
            payment_obj,
            self.initial_data.get('payment_expense_valid_list', [])
        )

        # create activity log for opportunity
        if payment_obj.opportunity_mapped:
            OpportunityActivityLogs.create_opportunity_log_application(
                tenant_id=payment_obj.tenant_id,
                company_id=payment_obj.company_id,
                opportunity_id=payment_obj.opportunity_mapped_id,
                employee_created_id=payment_obj.employee_created_id,
                app_code=str(payment_obj.__class__.get_model_code()),
                doc_id=payment_obj.id,
                title=payment_obj.title,
            )

        return payment_obj


class PaymentDetailSerializer(AbstractDetailSerializerModel):
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    employee_payment = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'id',
            'title',
            'code',
            'method',
            'date_created',
            'sale_code_type',
            'expense_items',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped',
            'supplier',
            'employee_payment',
            'is_internal_payment',
            'creator_name',
            'employee_inherit',
        )

    @classmethod
    def get_expense_items(cls, obj):
        all_expense_items_mapped = []
        for item in obj.payment.all():
            all_expense_items_mapped.append(
                {
                    'id': item.id,
                    'expense_type': {
                        'id': item.expense_type_id,
                        'code': item.expense_type.code,
                        'title': item.expense_type.title
                    } if item.expense_type else {},
                    'expense_description': item.expense_description,
                    'expense_uom_name': item.expense_uom_name,
                    'expense_quantity': item.expense_quantity,
                    'expense_unit_price': item.expense_unit_price,
                    'expense_tax': {
                        'id': item.expense_tax_id,
                        'code': item.expense_tax.code,
                        'title': item.expense_tax.title,
                        'rate': item.expense_tax.rate,
                    } if item.expense_tax else {},
                    'expense_tax_price': item.expense_tax_price,
                    'expense_subtotal_price': item.expense_subtotal_price,
                    'expense_after_tax_price': item.expense_after_tax_price,
                    'document_number': item.document_number,
                    'real_value': item.real_value,
                    'converted_value': item.converted_value,
                    'sum_value': item.sum_value,
                    'ap_cost_converted_list': item.ap_cost_converted_list
                }
            )
        return all_expense_items_mapped

    @classmethod
    def get_opportunity_mapped(cls, obj):
        return {
            'id': obj.opportunity_mapped_id,
            'code': obj.opportunity_mapped.code,
            'title': obj.opportunity_mapped.title,
            'customer': obj.opportunity_mapped.customer.name,
            'sale_order_mapped': {
                'id': obj.opportunity_mapped.sale_order_id,
                'code': obj.opportunity_mapped.sale_order.code,
                'title': obj.opportunity_mapped.sale_order.title,
            } if obj.opportunity_mapped.sale_order else {},
            'quotation_mapped': {
                'id': obj.opportunity_mapped.quotation_id,
                'code': obj.opportunity_mapped.quotation.code,
                'title': obj.opportunity_mapped.quotation.title,
            } if obj.opportunity_mapped.quotation else {}
        } if obj.opportunity_mapped else {}

    @classmethod
    def get_quotation_mapped(cls, obj):
        return {
            'id': obj.quotation_mapped_id,
            'code': obj.quotation_mapped.code,
            'title': obj.quotation_mapped.title,
            'customer': obj.quotation_mapped.customer.name,
        } if obj.quotation_mapped else {}

    @classmethod
    def get_sale_order_mapped(cls, obj):
        return {
            'id': obj.sale_order_mapped_id,
            'code': obj.sale_order_mapped.code,
            'title': obj.sale_order_mapped.title,
            'customer': obj.sale_order_mapped.customer.name,
            'quotation_mapped': {
                'id': obj.sale_order_mapped.quotation_id,
                'code': obj.sale_order_mapped.quotation.code,
                'title': obj.sale_order_mapped.quotation.title,
            } if obj.sale_order_mapped.quotation else {}
        } if obj.sale_order_mapped else {}

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            bank_accounts_mapped_list = []
            for item in obj.supplier.account_banks_mapped.all():
                bank_accounts_mapped_list.append(
                    {
                        'bank_country_id': item.country_id,
                        'bank_name': item.bank_name,
                        'bank_code': item.bank_code,
                        'bank_account_name': item.bank_account_name,
                        'bank_account_number': item.bank_account_number,
                        'bic_swift_code': item.bic_swift_code,
                        'is_default': item.is_default
                    }
                )
            return {
                'id': obj.supplier_id,
                'code': obj.supplier.code,
                'name': obj.supplier.name,
                'owner': {
                    'id': obj.supplier.owner_id,
                    'fullname': obj.supplier.owner.fullname
                } if obj.supplier.owner else {},
                'industry': {
                    'id': obj.supplier.industry_id,
                    'title': obj.supplier.industry.title
                } if obj.supplier.industry else {},
                'bank_accounts_mapped': bank_accounts_mapped_list
            }
        return {}

    @classmethod
    def get_employee_payment(cls, obj):
        if obj.employee_payment:
            return {
                'id': obj.employee_payment_id,
                'code': obj.employee_payment.code,
                'full_name': obj.employee_payment.get_full_name(2),
                'group': {
                    'id': obj.employee_payment.group_id,
                    'title': obj.employee_payment.group.title,
                    'code': obj.employee_payment.group.code,
                } if obj.employee_payment.group else {}
            }
        return {}

    @classmethod
    def get_creator_name(cls, obj):
        return {
            'id': obj.creator_name_id,
            'first_name': obj.creator_name.first_name,
            'last_name': obj.creator_name.last_name,
            'email': obj.creator_name.email,
            'full_name': obj.creator_name.get_full_name(2),
            'code': obj.creator_name.code,
            'is_active': obj.creator_name.is_active,
            'group': {
                'id': obj.creator_name.group_id,
                'title': obj.creator_name.group.title,
                'code': obj.creator_name.group.code
            } if obj.creator_name.group else {}
        } if obj.creator_name else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
            'group': {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title,
                'code': obj.employee_inherit.group.code
            } if obj.employee_inherit.group else {}
        } if obj.employee_inherit else {}


class PaymentUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Payment
        fields = (
            'title',
            'supplier',
            'employee_payment',
            'is_internal_payment',
            'method',
            # system
            'system_status',
        )

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError({'Method': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    def validate(self, validate_data):
        if validate_data.get('is_internal_payment'):
            if 'supplier' in validate_data:
                validate_data.pop('supplier')
        else:
            if 'employee_payment' in validate_data:
                validate_data.pop('employee_payment')
        return validate_data

    def update(self, instance, validated_data):
        if instance.opportunity_mapped:
            if instance.opportunity_mapped.is_close_lost or instance.opportunity_mapped.is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_payment_cost_items(
            instance,
            self.initial_data.get('payment_expense_valid_list', [])
        )
        return instance


class PaymentConfigListSerializer(serializers.ModelSerializer):
    employee_allowed = serializers.SerializerMethodField()

    class Meta:
        model = PaymentConfig
        fields = ('employee_allowed',)

    @classmethod
    def get_employee_allowed(cls, obj):
        return {
            'id': obj.employee_allowed_id,
            'code': obj.employee_allowed.code,
            'full_name': obj.employee_allowed.get_full_name(2)
        } if obj.employee_allowed else {}


class PaymentConfigUpdateSerializer(serializers.ModelSerializer):
    employees_allowed_list = serializers.ListSerializer(child=serializers.UUIDField(), required=False)
    employee_allowed = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PaymentConfig
        fields = (
            'employees_allowed_list',
            'employee_allowed'
        )

    def create(self, validated_data):
        bulk_info = []
        company_current = self.context.get('company_current', None)
        for item in self.initial_data.get('employees_allowed_list', []):
            bulk_info.append(PaymentConfig(employee_allowed_id=item, company=company_current))
        PaymentConfig.objects.filter(company=company_current).delete()
        objs = PaymentConfig.objects.bulk_create(bulk_info)
        return objs[0]


class PaymentConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentConfig
        fields = '__all__'


class PaymentCostListSerializer(serializers.ModelSerializer):
    expense_type = serializers.SerializerMethodField()

    class Meta:
        model = PaymentCost
        fields = (
            'expense_type',
            'real_value',
            'converted_value'
        )

    @classmethod
    def get_expense_type(cls, obj):
        return {
            'id': obj.expense_type_id,
            'code': obj.expense_type.code,
            'title': obj.expense_type.title
        } if obj.expense_type else {}
