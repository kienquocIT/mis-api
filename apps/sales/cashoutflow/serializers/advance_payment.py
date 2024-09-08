from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import (
    AdvancePayment, AdvancePaymentCost
)
from apps.masterdata.saledata.models import Currency, ExpenseItem
from apps.sales.cashoutflow.models.advance_payment import AdvancePaymentAttachmentFile
from apps.shared import (
    AdvancePaymentMsg, ProductMsg, SaleMsg, AbstractDetailSerializerModel,
    AbstractListSerializerModel, AbstractCreateSerializerModel
)


class AdvancePaymentListSerializer(AbstractListSerializerModel):
    advance_payment_type = serializers.SerializerMethodField()
    to_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    remain_value = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    opportunity_id = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

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
            'employee_inherit',
            'sale_order_mapped',
            'quotation_mapped',
            'opportunity_mapped',
            'expense_items',
            'opportunity_id',
            'system_status',
        )

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}

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


class AdvancePaymentCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'sale_code_type',
            'advance_payment_type',
            'supplier',
            'method',
            'employee_inherit_id',
            'return_date',
            'money_gave',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped'
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
        if validate_data.get('advance_payment_type') == 1 and not validate_data.get('supplier'):
            raise serializers.ValidationError({'Supplier': _('Supplier is required.')})
        if validate_data.get('advance_payment_type') == 0 and validate_data.get('supplier'):
            raise serializers.ValidationError({'Supplier': _('Supplier is not allowed.')})
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
        APCommonFunction.create_expense_items(ap_obj, self.initial_data.get('expense_valid_list', []))
        attachment = self.initial_data.get('attachment', '')
        if attachment:
            APCommonFunction.create_files_mapped(ap_obj, attachment.strip().split(','))
        return ap_obj


class AdvancePaymentDetailSerializer(AbstractDetailSerializerModel):
    expense_items = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
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
            'advance_value_by_words',
            'advance_payment_type',
            'expense_items',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped',
            'supplier',
            'employee_created',
            'employee_inherit',
            'attachment',
            'sale_code'
        )

    @classmethod
    def get_expense_items(cls, obj):
        all_item = obj.advance_payment.all()
        expense_items = []
        order = 1
        for item in all_item:
            expense_items.append(
                {
                    'id': item.id,
                    'order': order,
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
            order += 1
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
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'first_name': obj.employee_created.first_name,
            'last_name': obj.employee_created.last_name,
            'email': obj.employee_created.email,
            'full_name': obj.employee_created.get_full_name(2),
            'code': obj.employee_created.code,
            'is_active': obj.employee_created.is_active,
            'group': {
                'id': obj.employee_created.group_id,
                'title': obj.employee_created.group.title,
                'code': obj.employee_created.group.code
            } if obj.employee_created.group else {}
        } if obj.employee_created else {}

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


class AdvancePaymentUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'advance_payment_type',
            'supplier',
            'method',
            'return_date',
            'money_gave'
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
        if validate_data.get('advance_payment_type') == 1 and not validate_data.get('supplier'):
            raise serializers.ValidationError({'Supplier': _('Supplier is required.')})
        if validate_data.get('advance_payment_type') == 0 and validate_data.get('supplier'):
            raise serializers.ValidationError({'Supplier': _('Supplier is not allowed.')})
        if self.initial_data.get('expense_valid_list', []):
            if not ExpenseItem.objects.filter(
                    id__in=[item.get('expense_type_id', None) for item in self.initial_data['expense_valid_list']]
            ).exists():
                raise serializers.ValidationError({'Expense type': ProductMsg.DOES_NOT_EXIST})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        if instance.opportunity_mapped:
            if instance.opportunity_mapped.is_close_lost or instance.opportunity_mapped.is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        APCommonFunction.create_expense_items(instance, self.initial_data.get('expense_valid_list', []))

        attachment = self.initial_data.get('attachment', '')
        if attachment:
            APCommonFunction.create_files_mapped(instance, attachment.strip().split(','))
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


class APCommonFunction:
    @classmethod
    def read_money_vnd(cls, num):
        text1 = ' mươi'
        text2 = ' trăm'

        xe0 = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
        xe1 = ['', 'mười'] + [f'{pre}{text1}' for pre in xe0[2:]]
        xe2 = [''] + [f'{pre}{text2}' for pre in xe0[1:]]

        result = ""
        str_n = str(num)
        len_n = len(str_n)

        if len_n == 1:
            result = xe0[num]
        elif len_n == 2:
            if num == 10:
                result = "mười"
            else:
                result = xe1[int(str_n[0])] + " " + xe0[int(str_n[1])]
        elif len_n == 3:
            result = xe2[int(str_n[0])] + " " + cls.read_money_vnd(int(str_n[1:]))
        elif len_n <= 6:
            result = cls.read_money_vnd(int(str_n[:-3])) + " nghìn " + cls.read_money_vnd(int(str_n[-3:]))
        elif len_n <= 9:
            result = cls.read_money_vnd(int(str_n[:-6])) + " triệu " + cls.read_money_vnd(int(str_n[-6:]))
        elif len_n <= 12:
            result = cls.read_money_vnd(int(str_n[:-9])) + " tỷ " + cls.read_money_vnd(int(str_n[-9:]))

        return str(result.strip()).lower()

    @classmethod
    def create_expense_items(cls, advance_payment_obj, expense_valid_list):
        vnd_currency = Currency.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            abbreviation='VND'
        ).first()
        if vnd_currency:
            bulk_info = []
            advance_value = 0
            for item in expense_valid_list:
                advance_value += item.get('expense_after_tax_price', 0)
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
                advance_payment_obj.advance_value = advance_value
                advance_value_by_words = APCommonFunction.read_money_vnd(advance_value).capitalize()
                if advance_value_by_words[-1] == ',':
                    advance_value_by_words = advance_value_by_words[:-1] + ' đồng'
                advance_payment_obj.advance_value_by_words = advance_value_by_words

                opp = advance_payment_obj.opportunity_mapped
                quotation = advance_payment_obj.quotation_mapped
                sale_order = advance_payment_obj.sale_order_mapped
                sale_code = sale_order.code if (
                    sale_order) else quotation.code if quotation else opp.code if opp else None
                advance_payment_obj.sale_code = sale_code

                advance_payment_obj.save(update_fields=['advance_value', 'advance_value_by_words', 'sale_code'])
            return True
        return False

    @classmethod
    def create_files_mapped(cls, ap_obj, file_id_list):
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
