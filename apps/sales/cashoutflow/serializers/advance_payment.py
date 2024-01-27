from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import (
    AdvancePayment, AdvancePaymentCost
)
from apps.masterdata.saledata.models import Currency, ExpenseItem
from apps.sales.cashoutflow.models.advance_payment import AdvancePaymentAttachmentFile
from apps.sales.opportunity.models import OpportunityActivityLogs
from apps.shared import AdvancePaymentMsg, ProductMsg, SaleMsg, AbstractDetailSerializerModel


class AdvancePaymentListSerializer(serializers.ModelSerializer):
    advance_payment_type = serializers.SerializerMethodField()
    advance_value = serializers.SerializerMethodField()
    to_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    remain_value = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    opportunity_id = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
            'advance_payment_type',
            'date_created',
            'return_date',
            'advance_value',
            'to_payment',
            'return_value',
            'remain_value',
            'money_gave',
            'creator_name_id',
            'employee_inherit_id',
            'sale_order_mapped',
            'quotation_mapped',
            'opportunity_mapped',
            'expense_items',
            'opportunity_id',
            'system_status'
        )

    @classmethod
    def get_sale_order_mapped(cls, obj):
        if obj.sale_order_mapped:
            is_close = False
            if obj.sale_order_mapped.opportunity:
                if obj.sale_order_mapped.opportunity.is_close_lost or obj.sale_order_mapped.opportunity.is_deal_close:
                    is_close = True
                return {
                    'id': obj.sale_order_mapped_id,
                    'code': obj.sale_order_mapped.code,
                    'title': obj.sale_order_mapped.title,
                    'opportunity_id': obj.sale_order_mapped.opportunity_id,
                    'opportunity_code': obj.sale_order_mapped.opportunity.is_deal_close,
                    'is_close': is_close
                }
            return {
                'id': obj.sale_order_mapped_id,
                'code': obj.sale_order_mapped.code,
                'title': obj.sale_order_mapped.title,
                'opportunity_id': None,
                'opportunity_code': None,
                'is_close': is_close
            }
        return {}

    @classmethod
    def get_quotation_mapped(cls, obj):
        if obj.quotation_mapped:
            is_close = False
            if obj.quotation_mapped.opportunity:
                if obj.quotation_mapped.opportunity.is_close_lost or obj.quotation_mapped.opportunity.is_deal_close:
                    is_close = True
                return {
                    'id': obj.quotation_mapped_id,
                    'code': obj.quotation_mapped.code,
                    'title': obj.quotation_mapped.title,
                    'opportunity_id': obj.quotation_mapped.opportunity_id,
                    'opportunity_code': obj.quotation_mapped.opportunity.code,
                    'is_close': is_close,
                }
            return {
                'id': obj.quotation_mapped_id,
                'code': obj.quotation_mapped.code,
                'title': obj.quotation_mapped.title,
                'opportunity_id': None,
                'opportunity_code': None,
                'is_close': is_close,
            }
        return {}

    @classmethod
    def get_opportunity_mapped(cls, obj):
        if obj.opportunity_mapped:
            is_close = False
            if obj.opportunity_mapped.is_close_lost or obj.opportunity_mapped.is_deal_close:
                is_close = True
            return {
                'id': obj.opportunity_mapped_id,
                'code': obj.opportunity_mapped.code,
                'title': obj.opportunity_mapped.title,
                'is_close': is_close
            }
        return {}

    @classmethod
    def get_expense_items(cls, obj):
        all_item = obj.advance_payment.all()
        expense_items = []
        for item in all_item:
            expense_items.append(
                {
                    'id': item.id,
                    'expense_name': item.expense_name,
                    'expense_type': {
                        'id': item.expense_type_id,
                        'code': item.expense_type.code,
                        'title': item.expense_type.title,
                    } if item.expense_type else {},
                    'expense_uom_name': item.expense_uom_name,
                    'expense_quantity': item.expense_quantity,
                    'expense_unit_price': item.expense_unit_price,
                    'expense_tax': {
                        'id': item.expense_tax_id,
                        'code': item.expense_tax.code,
                        'title': item.expense_tax.title,
                        'rate': item.expense_tax.rate
                    } if item.expense_tax else {},
                    'expense_tax_price': item.expense_tax_price,
                    'expense_subtotal_price': item.expense_subtotal_price,
                    'expense_after_tax_price': item.expense_after_tax_price,
                }
            )
        return expense_items

    @classmethod
    def get_advance_payment_type(cls, obj):
        if obj.advance_payment_type:
            return "To Supplier"
        return "To Employee"

    @classmethod
    def get_advance_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_ap_value = sum(item.expense_after_tax_price for item in all_items)
        return sum_ap_value

    @classmethod
    def get_to_payment(cls, obj):
        all_items = obj.advance_payment.all()
        sum_payment_converted_value = sum(item.sum_converted_value for item in all_items)
        return sum_payment_converted_value

    @classmethod
    def get_return_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_return_value = sum(item.sum_return_value for item in all_items)
        return sum_return_value

    @classmethod
    def get_remain_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_ap_value = sum(item.expense_after_tax_price for item in all_items)
        sum_return_value = sum(item.sum_return_value for item in all_items)
        sum_payment_converted_value = sum(item.sum_converted_value for item in all_items)
        return sum_ap_value - sum_return_value - sum_payment_converted_value

    @classmethod
    def get_opportunity_id(cls, obj):
        if obj.opportunity_mapped:
            return obj.opportunity_mapped_id
        if obj.quotation_mapped:
            return obj.quotation_mapped.opportunity_id
        if obj.sale_order_mapped:
            return obj.sale_order_mapped.opportunity_id
        return None


def create_expense_items(advance_payment_obj, expense_valid_list):
    vnd_currency = Currency.objects.filter_current(
        fill__tenant=True,
        fill__company=True,
        abbreviation='VND'
    ).first()
    if vnd_currency:
        bulk_info = []
        for item in expense_valid_list:
            bulk_info.append(AdvancePaymentCost(
                **item,
                advance_payment=advance_payment_obj,
                sale_order_mapped=advance_payment_obj.sale_order_mapped,
                quotation_mapped=advance_payment_obj.quotation_mapped,
                opportunity_mapped=advance_payment_obj.opportunity_mapped,
                currency=vnd_currency
            ))
        if len(bulk_info) > 0:
            AdvancePaymentCost.objects.filter(advance_payment=advance_payment_obj).delete()
            AdvancePaymentCost.objects.bulk_create(bulk_info)
        return True
    return False


def create_files_mapped(ap_obj, file_id_list):
    try:
        bulk_data_file = []
        for index, file_id in enumerate(file_id_list):
            bulk_data_file.append(AdvancePaymentAttachmentFile(
                advance_payment=ap_obj,
                attachment_id=file_id,
                order=index
            ))
        AdvancePaymentAttachmentFile.objects.filter(advance_payment=ap_obj).delete()
        AdvancePaymentAttachmentFile.objects.bulk_create(bulk_data_file)
        return True
    except Exception as err:
        raise serializers.ValidationError({'files': SaleMsg.SAVE_FILES_ERROR + f' {err}'})


class AdvancePaymentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'sale_code_type',
            'advance_payment_type',
            'supplier',
            'method',
            'creator_name',
            'employee_inherit',
            'return_date',
            'money_gave',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped',
            'system_status'
        )

    @classmethod
    def validate_sale_code_type(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError({'Sale code type': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    @classmethod
    def validate_advance_payment_type(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError({'Advance payment type': AdvancePaymentMsg.TYPE_ERROR})

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError({'Method': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    def validate(self, validate_data):
        if self.initial_data.get('expense_valid_list', []):
            if not ExpenseItem.objects.filter(
                    id__in=[item.get('expense_type_id', None) for item in self.initial_data['expense_valid_list']]
            ).exists():
                raise serializers.ValidationError({'Expense type': ProductMsg.DOES_NOT_EXIST})
        if validate_data.get('opportunity_mapped', None):
            if validate_data['opportunity_mapped'].is_close_lost or validate_data['opportunity_mapped'].is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        ap_obj = AdvancePayment.objects.create(**validated_data)
        create_expense_items(ap_obj, self.initial_data.get('expense_valid_list', []))
        # create activity log for opportunity
        if ap_obj.opportunity_mapped:
            OpportunityActivityLogs.create_opportunity_log_application(
                tenant_id=ap_obj.tenant_id,
                company_id=ap_obj.company_id,
                opportunity_id=ap_obj.opportunity_mapped_id,
                employee_created_id=ap_obj.employee_created_id,
                app_code=str(ap_obj.__class__.get_model_code()),
                doc_id=ap_obj.id,
                title=ap_obj.title,
            )

        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(ap_obj, attachment.strip().split(','))
        return ap_obj


class AdvancePaymentDetailSerializer(AbstractDetailSerializerModel):
    expense_items = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    advance_value = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
            'method',
            'money_gave',
            'date_created',
            'return_date',
            'sale_code_type',
            'advance_value',
            'advance_payment_type',
            'expense_items',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped',
            'supplier',
            'creator_name',
            'employee_inherit',
            'attachment'
        )

    @classmethod
    def get_advance_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_ap_value = sum(item.expense_after_tax_price for item in all_items)
        return sum_ap_value

    @classmethod
    def get_expense_items(cls, obj):
        all_item = obj.advance_payment.all()
        expense_items = []
        for item in all_item:
            expense_items.append(
                {
                    'id': item.id,
                    'expense_name': item.expense_name,
                    'expense_type': {
                        'id': item.expense_type_id,
                        'code': item.expense_type.code,
                        'title': item.expense_type.title,
                    } if item.expense_type else {},
                    'expense_uom_name': item.expense_uom_name,
                    'expense_quantity': item.expense_quantity,
                    'expense_unit_price': item.expense_unit_price,
                    'expense_tax': {
                        'id': item.expense_tax_id,
                        'code': item.expense_tax.code,
                        'title': item.expense_tax.title,
                        'rate': item.expense_tax.rate
                    } if item.expense_tax else {},
                    'expense_tax_price': item.expense_tax_price,
                    'expense_subtotal_price': item.expense_subtotal_price,
                    'expense_after_tax_price': item.expense_after_tax_price,
                    'remain_total': item.expense_after_tax_price - item.sum_return_value - item.sum_converted_value
                }
            )
        return expense_items

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

    @classmethod
    def get_attachment(cls, obj):
        att_objs = AdvancePaymentAttachmentFile.objects.select_related('attachment').filter(advance_payment=obj)
        return [item.attachment.get_detail() for item in att_objs]


class AdvancePaymentUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'advance_payment_type',
            'supplier',
            'method',
            'return_date',
            'money_gave',
            'system_status',
        )

    @classmethod
    def validate_advance_payment_type(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError({'Advance payment type': AdvancePaymentMsg.TYPE_ERROR})

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError({'Method': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    def validate(self, validate_data):
        if self.initial_data.get('expense_valid_list', []):
            if not ExpenseItem.objects.filter(
                    id__in=[item.get('expense_type_id', None) for item in self.initial_data['expense_valid_list']]
            ).exists():
                raise serializers.ValidationError({'Expense type': ProductMsg.DOES_NOT_EXIST})
        return validate_data

    def update(self, instance, validated_data):
        if instance.opportunity_mapped:
            if instance.opportunity_mapped.is_close_lost or instance.opportunity_mapped.is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_expense_items(instance, self.initial_data.get('expense_valid_list', []))

        attachment = self.initial_data.get('attachment', '')
        if attachment:
            create_files_mapped(instance, attachment.strip().split(','))
        return instance


class AdvancePaymentCostListSerializer(serializers.ModelSerializer):
    expense_type = serializers.SerializerMethodField()
    expense_tax = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePaymentCost
        fields = (
            'expense_name',
            'expense_type',
            'expense_uom_name',
            'expense_quantity',
            'expense_unit_price',
            'expense_tax',
            'expense_tax_price',
            'expense_subtotal_price',
            'expense_after_tax_price',
            'sum_return_value',
            'sum_converted_value',
        )

    @classmethod
    def get_expense_type(cls, obj):
        if obj.expense_type:
            return {'id': obj.expense_type_id, 'code': obj.expense_type.code, 'title': obj.expense_type.title}
        return {}

    @classmethod
    def get_expense_tax(cls, obj):
        if obj.expense_tax:
            return {'id': obj.expense_tax_id, 'code': obj.expense_tax.code, 'title': obj.expense_tax.title}
        return {}
