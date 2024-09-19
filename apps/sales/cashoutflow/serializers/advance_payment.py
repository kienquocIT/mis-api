from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import AdvancePayment, AdvancePaymentCost
from apps.masterdata.saledata.models import Currency, ExpenseItem, Account, Tax
from apps.sales.cashoutflow.models.advance_payment import AdvancePaymentAttachmentFile
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrder
from apps.shared import (
    AdvancePaymentMsg, SaleMsg, AbstractDetailSerializerModel,
    AbstractListSerializerModel, AbstractCreateSerializerModel, HRMsg
)
from apps.shared.translations.base import AttachmentMsg


class AdvancePaymentListSerializer(AbstractListSerializerModel):
    advance_payment_type = serializers.SerializerMethodField()
    to_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    remain_value = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    opportunity_id = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
            'money_gave',
            'date_created',
            'return_date',
            'advance_value',
            'sale_code',
            'system_status',
            # custom,
            'advance_payment_type',
            'to_payment',
            'return_value',
            'remain_value',
            'opportunity_mapped',
            'quotation_mapped',
            'sale_order_mapped',
            'employee_inherit',
            'opportunity_id',
            'expense_items',
        )

    @classmethod
    def get_advance_payment_type(cls, obj):
        return obj.advance_payment_type

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
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}

    @classmethod
    def get_opportunity_id(cls, obj):
        if obj.opportunity_mapped:
            return obj.opportunity_mapped_id
        if obj.quotation_mapped:
            return obj.quotation_mapped.opportunity_id
        if obj.sale_order_mapped:
            return obj.sale_order_mapped.opportunity_id
        return None

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


class AdvancePaymentCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)
    opportunity_mapped_id = serializers.UUIDField(required=False, allow_null=True)
    quotation_mapped_id = serializers.UUIDField(required=False, allow_null=True)
    sale_order_mapped_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField()
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    ap_item_list = serializers.ListField(required=False, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'opportunity_mapped_id',
            'quotation_mapped_id',
            'sale_order_mapped_id',
            'sale_code_type',
            'employee_inherit_id',
            'advance_payment_type',
            'supplier_id',
            'method',
            'return_date',
            'money_gave',
            'ap_item_list',
            'attachment'
        )

    def validate(self, validate_data):
        APCommonFunction.validate_opportunity_mapped_id(validate_data)
        APCommonFunction.validate_quotation_mapped_id(validate_data)
        APCommonFunction.validate_sale_order_mapped_id(validate_data)
        APCommonFunction.validate_sale_code_type(validate_data)
        APCommonFunction.validate_employee_inherit_id(validate_data)
        APCommonFunction.validate_advance_payment_type(validate_data)
        APCommonFunction.validate_method(validate_data)
        APCommonFunction.validate_ap_item_list(validate_data)
        APCommonFunction.validate_common(validate_data)
        APCommonFunction.validate_attachment(
            context_user=self.context.get('user', None),
            doc_id=None,
            validate_data=validate_data
        )
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        ap_item_list = validated_data.pop('ap_item_list', [])
        attachment = validated_data.pop('attachment', [])

        ap_obj = AdvancePayment.objects.create(**validated_data)
        APCommonFunction.create_ap_items(ap_obj, ap_item_list)
        APCommonFunction.handle_attach_file(ap_obj, attachment)
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
        expense_items = []
        order = 1
        for item in obj.advance_payment.all():
            expense_items.append({
                'id': item.id,
                'order': order,
                'expense_name': item.expense_name,
                'expense_type': item.expense_type_data,
                'expense_uom_name': item.expense_uom_name,
                'expense_quantity': item.expense_quantity,
                'expense_unit_price': item.expense_unit_price,
                'expense_tax': item.expense_tax_data,
                'expense_tax_price': item.expense_tax_price,
                'expense_subtotal_price': item.expense_subtotal_price,
                'expense_after_tax_price': item.expense_after_tax_price,
                'remain_total': item.expense_after_tax_price - item.sum_return_value - item.sum_converted_value
            })
            order += 1
        return expense_items

    @classmethod
    def get_opportunity_mapped(cls, obj):
        return {
            'id': str(obj.opportunity_mapped.id),
            'code': obj.opportunity_mapped.code,
            'title': obj.opportunity_mapped.title,
            'customer': obj.opportunity_mapped.customer.name if obj.opportunity_mapped.customer else '',
            'sale_order_mapped': {
                'id': str(obj.opportunity_mapped.sale_order_id),
                'code': obj.opportunity_mapped.sale_order.code,
                'title': obj.opportunity_mapped.sale_order.title,
            } if obj.opportunity_mapped.sale_order else {},
            'quotation_mapped': {
                'id': str(obj.opportunity_mapped.quotation_id),
                'code': obj.opportunity_mapped.quotation.code,
                'title': obj.opportunity_mapped.quotation.title,
            } if obj.opportunity_mapped.quotation else {}
        } if obj.opportunity_mapped else {}

    @classmethod
    def get_quotation_mapped(cls, obj):
        return {
            'id': str(obj.quotation_mapped.id),
            'code': obj.quotation_mapped.code,
            'title': obj.quotation_mapped.title,
            'customer': obj.quotation_mapped.customer.name if obj.quotation_mapped.customer else '',
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
        return {
            'id': str(obj.supplier.id),
            'code': obj.supplier.code,
            'name': obj.supplier.name,
            'owner': {
                'id': str(obj.supplier.owner_id),
                'fullname': obj.supplier.owner.fullname
            } if obj.supplier.owner else {},
            'industry': {
                'id': str(obj.supplier.industry_id),
                'title': obj.supplier.industry.title
            } if obj.supplier.industry else {},
            'bank_accounts_mapped': [{
                'bank_country_id': str(item.country_id),
                'bank_name': item.bank_name,
                'bank_code': item.bank_code,
                'bank_account_name': item.bank_account_name,
                'bank_account_number': item.bank_account_number,
                'bic_swift_code': item.bic_swift_code,
                'is_default': item.is_default
            } for item in obj.supplier.account_banks_mapped.all()]
        } if obj.supplier else {}

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
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    ap_item_list = serializers.ListField(required=False, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'advance_payment_type',
            'supplier_id',
            'method',
            'return_date',
            'money_gave',
            'ap_item_list',
            'attachment'
        )

    def validate(self, validate_data):
        APCommonFunction.validate_advance_payment_type(validate_data)
        APCommonFunction.validate_method(validate_data)
        APCommonFunction.validate_ap_item_list(validate_data)
        APCommonFunction.validate_common(validate_data)
        APCommonFunction.validate_attachment(
            context_user=self.context.get('user', None),
            doc_id=self.instance.id,
            validate_data=validate_data
        )
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        ap_item_list = validated_data.pop('ap_item_list', [])
        attachment = validated_data.pop('attachment', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        APCommonFunction.create_ap_items(instance, ap_item_list)
        APCommonFunction.handle_attach_file(instance, attachment)
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
    def validate_opportunity_mapped_id(cls, validate_data):
        if validate_data.get('opportunity_mapped_id'):
            try:
                opportunity_mapped = Opportunity.objects.get(id=validate_data.get('opportunity_mapped_id'))
                if opportunity_mapped.is_close_lost or opportunity_mapped.is_deal_close:
                    raise serializers.ValidationError({'opportunity_mapped_id': SaleMsg.OPPORTUNITY_CLOSED})
                validate_data['opportunity_mapped_id'] = str(opportunity_mapped.id)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity_mapped_id': 'Opportunity is not exist.'})
        else:
            validate_data['opportunity_mapped_id'] = None
        print('1. validate_opportunity_mapped_id --- ok')
        return validate_data

    @classmethod
    def validate_quotation_mapped_id(cls, validate_data):
        if validate_data.get('quotation_mapped_id'):
            try:
                quotation_mapped = Quotation.objects.get(id=validate_data.get('quotation_mapped_id'))
                validate_data['quotation_mapped_id'] = str(quotation_mapped.id)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'quotation_mapped_id': 'Quotation is not exist.'})
        else:
            validate_data['quotation_mapped_id'] = None
        print('2. validate_quotation_mapped_id --- ok')
        return validate_data

    @classmethod
    def validate_sale_order_mapped_id(cls, validate_data):
        if validate_data.get('sale_order_mapped_id'):
            try:
                sale_order_mapped = SaleOrder.objects.get(id=validate_data.get('sale_order_mapped_id'))
                validate_data['sale_order_mapped_id'] = str(sale_order_mapped.id)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'sale_order_mapped_id': 'Sale order is not exist.'})
        else:
            validate_data['sale_order_mapped_id'] = None
        print('3. validate_sale_order_mapped_id --- ok')
        return validate_data

    @classmethod
    def validate_sale_code_type(cls, validate_data):
        if validate_data.get('sale_code_type'):
            if validate_data.get('sale_code_type') not in [0, 1, 2]:
                raise serializers.ValidationError({'sale_code_type': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})
        print('4. validate_sale_code_type --- ok')
        return validate_data

    @classmethod
    def validate_employee_inherit_id(cls, validate_data):
        if validate_data.get('employee_inherit_id'):
            try:
                validate_data['employee_inherit_id'] = str(Employee.objects.get(
                    id=validate_data.get('employee_inherit_id')
                ).id)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({'employee_inherit_id': 'Employee inherit is not exist'})
        print('5. validate_employee_inherit_id --- ok')
        return validate_data

    @classmethod
    def validate_advance_payment_type(cls, validate_data):
        if validate_data.get('advance_payment_type'):
            if validate_data.get('advance_payment_type') not in [0, 1]:
                raise serializers.ValidationError({'advance_payment_type': AdvancePaymentMsg.TYPE_ERROR})
        print('6. validate_advance_payment_type --- ok')
        return validate_data

    @classmethod
    def validate_supplier_id(cls, validate_data):
        if validate_data.get('supplier_id'):
            try:
                supplier = Account.objects.get(id=validate_data.get('supplier_id'))
                validate_data['supplier_id'] = str(supplier.id)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'supplier_id': 'Supplier is not exist.'})
        else:
            validate_data['supplier_id'] = None
        print('7. validate_supplier_id --- ok')
        return validate_data

    @classmethod
    def validate_method(cls, validate_data):
        if validate_data.get('method'):
            if validate_data.get('method') not in [0, 1]:
                raise serializers.ValidationError({'method': 'Method is not valid.'})
        print('8. validate_method --- ok')
        return validate_data

    @classmethod
    def validate_ap_item_list(cls, validate_data):
        try:
            for item in validate_data.get('ap_item_list', []):
                if not all([
                    item.get('expense_name'),
                    item.get('expense_uom_name'),
                    float(item.get('expense_quantity', 0)) > 0,
                    float(item.get('expense_unit_price')) > 0,
                    float(item.get('expense_tax_price', 0)) >= 0,
                ]):
                    raise serializers.ValidationError({'ap_item_list': 'AP item list is not valid.'})

                expense_type = ExpenseItem.objects.get(id=item.get('expense_type_id'))
                item['expense_type_id'] = str(expense_type.id)
                item['expense_type_data'] = {
                    'id': str(expense_type.id),
                    'code': expense_type.code,
                    'title': expense_type.title
                } if expense_type else {}
                if item.get('expense_tax_id'):
                    expense_tax = Tax.objects.get(id=item.get('expense_tax_id'))
                    item['expense_tax_id'] = str(expense_tax.id)
                    item['expense_tax_data'] = {
                        'id': str(expense_tax.id),
                        'code': expense_tax.code,
                        'title': expense_tax.title,
                        'rate': expense_tax.rate
                    } if expense_tax else {}
                item['expense_subtotal_price'] = (
                        float(item['expense_quantity']) * float(item['expense_unit_price'])
                )
                item['expense_after_tax_price'] = (
                        item['expense_subtotal_price'] + float(item.get('expense_tax_price', 0))
                )
            print('9. validate_ap_item_list --- ok')
            return validate_data
        except Exception as err:
            print(err)
            raise serializers.ValidationError({'ap_item_list': f'AP item list is not valid.'})

    @classmethod
    def validate_attachment(cls, context_user, doc_id, validate_data):
        if context_user and hasattr(context_user, 'employee_current_id'):
            state, result = AdvancePaymentAttachmentFile.valid_change(
                current_ids=validate_data.get('attachment', []),
                employee_id=context_user.employee_current_id,
                doc_id=doc_id
            )
            if state is True:
                validate_data['attachment'] = result
                print('10. validate_attachment --- ok')
                return validate_data
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_common(cls, validate_data):
        if validate_data.get('advance_payment_type'):
            if validate_data.get('advance_payment_type') == 1 and not validate_data.get('supplier_id'):
                raise serializers.ValidationError({'supplier': _('Supplier is required.')})
            if validate_data.get('advance_payment_type') == 0 and validate_data.get('supplier_id'):
                raise serializers.ValidationError({'supplier_id': _('Supplier is not allowed.')})
        return validate_data

    @classmethod
    def read_money_vnd(cls, num):
        text1 = ' mươi'
        text2 = ' trăm'

        xe0 = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
        xe1 = ['', 'mười'] + [f'{pre}{text1}' for pre in xe0[2:]]
        xe2 = [''] + [f'{pre}{text2}' for pre in xe0[1:]]

        result = ""
        str_n = str(int(num))
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
    def create_ap_items(cls, advance_payment_obj, ap_item_list):
        vnd_currency = Currency.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            abbreviation='VND'
        ).first()
        if vnd_currency:
            bulk_info = []
            advance_value = 0
            for item in ap_item_list:
                advance_value += float(item.get('expense_after_tax_price', 0))
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
    def handle_attach_file(cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="57725469-8b04-428a-a4b0-578091d0e4f5").first()
            if relate_app:
                state = AdvancePaymentAttachmentFile.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True
