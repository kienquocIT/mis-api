from rest_framework import serializers
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.process.utils import ProcessRuntimeControl
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import (
    Payment, PaymentCost, PaymentConfig
)
from apps.masterdata.saledata.models import Currency, Account, ExpenseItem, Tax
from apps.sales.cashoutflow.models.payment import PaymentAttachmentFile
from apps.sales.opportunity.models import Opportunity
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrder
from apps.shared import AdvancePaymentMsg, AbstractDetailSerializerModel, SaleMsg, AbstractCreateSerializerModel, \
    AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg


class PaymentListSerializer(AbstractListSerializerModel):
    converted_value_list = serializers.SerializerMethodField()
    return_value_list = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'id',
            'code',
            'title',
            'sale_code_type',
            'supplier',
            'method',
            'sale_code',
            'employee_created',
            'employee_inherit',
            'return_value_list',
            'payment_value',
            'date_created',
            'system_status',
            'sale_order_mapped',
            'quotation_mapped',
            'opportunity_mapped',
            'converted_value_list'
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
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}


class PaymentCreateSerializer(AbstractCreateSerializerModel):
    opportunity_mapped_id = serializers.UUIDField(required=False, allow_null=True)
    quotation_mapped_id = serializers.UUIDField(required=False, allow_null=True)
    sale_order_mapped_id = serializers.UUIDField(required=False, allow_null=True)
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    employee_payment_id = serializers.UUIDField(required=False, allow_null=True)
    payment_item_list = serializers.ListField(required=False, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    process = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    class Meta:
        model = Payment
        fields = (
            # process
            'process',
            #
            'title',
            'opportunity_mapped_id',
            'quotation_mapped_id',
            'sale_order_mapped_id',
            'sale_code_type',
            'employee_inherit_id',
            'supplier_id',
            'is_internal_payment',
            'employee_payment_id',
            'method',
            'payment_item_list',
            'attachment'
        )

    def validate(self, validate_data):
        if all(key in validate_data for key in ['is_internal_payment', 'supplier_id', 'employee_payment_id']):
            if validate_data.get('is_internal_payment') is True:
                validate_data.pop('supplier_id', None)
                if not validate_data.get('employee_payment_id'):
                    raise serializers.ValidationError({'employee_payment_id': "Employee payment is missing."})
            else:
                validate_data.pop('employee_payment_id', None)
                if not validate_data.get('supplier_id'):
                    raise serializers.ValidationError({'supplier_id': "Supplier payment is missing."})
        PaymentCommonFunction.validate_opportunity_mapped_id(validate_data)
        PaymentCommonFunction.validate_quotation_mapped_id(validate_data)
        PaymentCommonFunction.validate_sale_order_mapped_id(validate_data)
        PaymentCommonFunction.validate_sale_code_type(validate_data)
        PaymentCommonFunction.validate_employee_inherit_id(validate_data)
        PaymentCommonFunction.validate_supplier_id(validate_data)
        PaymentCommonFunction.validate_employee_payment_id(validate_data)
        PaymentCommonFunction.validate_method(validate_data)
        PaymentCommonFunction.validate_payment_item_list(validate_data)
        PaymentCommonFunction.validate_common(validate_data)
        PaymentCommonFunction.validate_attachment(
            context_user=self.context.get('user', None),
            doc_id=None,
            validate_data=validate_data
        )

        process_obj = validate_data.get('process', None)
        opportunity_id = validate_data.get('opportunity_mapped_id', None)
        app_id = Payment.get_app_id()
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(opp_id=opportunity_id, app_id=app_id)

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        payment_item_list = validated_data.pop('payment_item_list', [])
        attachment = validated_data.pop('attachment', [])

        payment_obj = Payment.objects.create(**validated_data)
        PaymentCommonFunction.create_payment_items(payment_obj, payment_item_list)
        PaymentCommonFunction.handle_attach_file(payment_obj, attachment)

        if payment_obj.process:
            ProcessRuntimeControl(process_obj=payment_obj.process).register_doc(
                app_id=Payment.get_app_id(),
                doc_id=payment_obj.id,
                doc_title=payment_obj.title,
                employee_created_id=payment_obj.employee_created_id,
                date_created=payment_obj.date_created,
            )

        return payment_obj


class PaymentDetailSerializer(AbstractDetailSerializerModel):
    date_created = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    employee_payment = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()

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
            'employee_created',
            'employee_inherit',
            'attachment',
            'sale_code',
            'payment_value',
            'payment_value_by_words',
            # process
            'process',
        )

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
    def get_date_created(cls, obj):
        return obj.date_created.strftime('%d/%m/%Y')

    @classmethod
    def get_expense_items(cls, obj):
        all_expense_items_mapped = []
        order = 1
        for item in obj.payment.all():
            detail_payment = f"- Giá trị thanh toán: {item.real_value} {item.currency.abbreviation}.\n"
            detail_payment += "- Chuyển đổi từ Tạm ứng:\n" if len(item.ap_cost_converted_list) > 0 else ''
            for data in item.ap_cost_converted_list:
                detail_payment += (
                    f"+ {data.get('ap_title')} - {data.get('value_converted')} {item.currency.abbreviation}.\n"
                )
            detail_payment += f"(Tổng: {item.sum_value} {item.currency.abbreviation})"
            all_expense_items_mapped.append(
                {
                    'id': item.id,
                    'order': order,
                    'expense_type': item.expense_type_data,
                    'expense_description': item.expense_description,
                    'expense_uom_name': item.expense_uom_name,
                    'expense_quantity': item.expense_quantity,
                    'expense_unit_price': item.expense_unit_price,
                    'expense_tax': item.expense_tax_data,
                    'expense_tax_price': item.expense_tax_price,
                    'expense_subtotal_price': item.expense_subtotal_price,
                    'expense_after_tax_price': item.expense_after_tax_price,
                    'document_number': item.document_number,
                    'real_value': item.real_value,
                    'converted_value': item.converted_value,
                    'sum_value': item.sum_value,
                    'ap_cost_converted_list': item.ap_cost_converted_list,
                    'detail_payment': detail_payment
                }
            )
            order += 1
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
        att_objs = PaymentAttachmentFile.objects.select_related('attachment').filter(payment=obj)
        return [item.attachment.get_detail() for item in att_objs]


class PaymentUpdateSerializer(AbstractCreateSerializerModel):
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    employee_payment_id = serializers.UUIDField(required=False, allow_null=True)
    payment_item_list = serializers.ListField(required=False, allow_null=True)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = Payment
        fields = (
            'title',
            'supplier_id',
            'is_internal_payment',
            'employee_payment_id',
            'method',
            'payment_item_list',
            'attachment'
        )

    def validate(self, validate_data):
        if all(key in validate_data for key in ['is_internal_payment', 'supplier_id', 'employee_payment_id']):
            if validate_data.get('is_internal_payment') is True:
                validate_data.pop('supplier_id', None)
                if not validate_data.get('employee_payment_id'):
                    raise serializers.ValidationError({'employee_payment_id': "Employee payment is missing."})
            else:
                validate_data.pop('employee_payment_id', None)
                if not validate_data.get('supplier_id'):
                    raise serializers.ValidationError({'supplier_id': "Supplier payment is missing."})
        PaymentCommonFunction.validate_supplier_id(validate_data)
        PaymentCommonFunction.validate_employee_payment_id(validate_data)
        PaymentCommonFunction.validate_method(validate_data)
        PaymentCommonFunction.validate_payment_item_list(validate_data)
        PaymentCommonFunction.validate_common(validate_data)
        PaymentCommonFunction.validate_attachment(
            context_user=self.context.get('user', None),
            doc_id=self.instance.id,
            validate_data=validate_data
        )
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        payment_item_list = validated_data.pop('payment_item_list', [])
        attachment = validated_data.pop('attachment', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        PaymentCommonFunction.create_payment_items(instance, payment_item_list)
        PaymentCommonFunction.handle_attach_file(instance, attachment)
        return instance


class PaymentCommonFunction:
    @classmethod
    def validate_opportunity_mapped_id(cls, validate_data):
        if 'opportunity_mapped_id' in validate_data:
            if validate_data.get('opportunity_mapped_id'):
                try:
                    opportunity_mapped = Opportunity.objects.get(id=validate_data.get('opportunity_mapped_id'))
                    if opportunity_mapped.is_close_lost or opportunity_mapped.is_deal_close:
                        raise serializers.ValidationError({'opportunity_mapped_id': SaleMsg.OPPORTUNITY_CLOSED})
                    validate_data['opportunity_mapped_id'] = str(opportunity_mapped.id)
                except Opportunity.DoesNotExist:
                    raise serializers.ValidationError({'opportunity_mapped_id': 'Opportunity does not exist.'})
            else:
                validate_data['opportunity_mapped_id'] = None
            print('1. validate_opportunity_mapped_id --- ok')
        return validate_data

    @classmethod
    def validate_quotation_mapped_id(cls, validate_data):
        if 'quotation_mapped_id' in validate_data:
            if validate_data.get('quotation_mapped_id'):
                try:
                    validate_data['quotation_mapped_id'] = str(Quotation.objects.get(
                        id=validate_data.get('quotation_mapped_id')
                    ).id)
                except Opportunity.DoesNotExist:
                    raise serializers.ValidationError({'quotation_mapped_id': 'Quotation does not exist.'})
            else:
                validate_data['quotation_mapped_id'] = None
            print('2. validate_quotation_mapped_id --- ok')
        return validate_data

    @classmethod
    def validate_sale_order_mapped_id(cls, validate_data):
        if 'sale_order_mapped_id' in validate_data:
            if validate_data.get('sale_order_mapped_id'):
                try:
                    validate_data['sale_order_mapped_id'] = str(SaleOrder.objects.get(
                        id=validate_data.get('sale_order_mapped_id')
                    ).id)
                except Opportunity.DoesNotExist:
                    raise serializers.ValidationError({'sale_order_mapped_id': 'Sale order does not exist.'})
            else:
                validate_data['sale_order_mapped_id'] = None
            print('3. validate_sale_order_mapped_id --- ok')
        return validate_data

    @classmethod
    def validate_sale_code_type(cls, validate_data):
        if 'sale_code_type' in validate_data:
            if validate_data.get('sale_code_type') not in [0, 1, 2]:
                raise serializers.ValidationError({'sale_code_type': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})
            print('4. validate_sale_code_type --- ok')
        return validate_data

    @classmethod
    def validate_employee_inherit_id(cls, validate_data):
        if 'employee_inherit_id' in validate_data:
            if validate_data.get('employee_inherit_id'):
                try:
                    validate_data['employee_inherit_id'] = str(Employee.objects.get(
                        id=validate_data.get('employee_inherit_id')
                    ).id)
                except Employee.DoesNotExist:
                    raise serializers.ValidationError({'employee_inherit_id': 'Employee inherit does not exist'})
            else:
                raise serializers.ValidationError({'employee_inherit_id': 'Employee inherit is not null'})
            print('5. validate_employee_inherit_id --- ok')
        return validate_data

    @classmethod
    def validate_supplier_id(cls, validate_data):
        if 'supplier_id' in validate_data:
            if validate_data.get('supplier_id'):
                try:
                    validate_data['supplier_id'] = str(Account.objects.get(id=validate_data.get('supplier_id')).id)
                except Opportunity.DoesNotExist:
                    raise serializers.ValidationError({'supplier_id': 'Supplier does not exist.'})
            else:
                validate_data['supplier_id'] = None
            print('6. validate_supplier_id --- ok')
        return validate_data

    @classmethod
    def validate_employee_payment_id(cls, validate_data):
        if 'employee_payment_id' in validate_data:
            if validate_data.get('employee_payment_id'):
                try:
                    validate_data['employee_payment_id'] = str(Employee.objects.get(
                        id=validate_data.get('employee_payment_id')
                    ).id)
                except Opportunity.DoesNotExist:
                    raise serializers.ValidationError({'employee_payment_id': 'Employee payment does not exist.'})
            else:
                validate_data['employee_payment_id'] = None
            print('7. validate_employee_payment_id --- ok')
        return validate_data

    @classmethod
    def validate_method(cls, validate_data):
        if 'method' in validate_data:
            if validate_data.get('method') not in [0, 1, 2]:
                raise serializers.ValidationError({'method': 'Method is not valid.'})
            print('8. validate_method --- ok')
        return validate_data

    @classmethod
    def validate_payment_item_list(cls, validate_data):
        try:
            for item in validate_data.get('payment_item_list', []):
                if not all([
                    item.get('expense_uom_name'),
                    float(item.get('expense_quantity', 0)) > 0,
                    float(item.get('expense_unit_price', 0)) > 0,
                    item.get('document_number'),
                    float(item.get('sum_value')) == float(item.get('expense_after_tax_price'))
                ]):
                    raise serializers.ValidationError({'payment_item_list': 'Tab Line detail is not valid.'})

                expense_type = ExpenseItem.objects.get(id=item.get('expense_type_id'))
                item['expense_type_id'] = str(expense_type.id)
                item['expense_type_data'] = {
                    'id': str(expense_type.id),
                    'code': expense_type.code,
                    'title': expense_type.title
                }
                if item.get('expense_tax_id'):
                    expense_tax = Tax.objects.get(id=item.get('expense_tax_id'))
                    item['expense_tax_id'] = str(expense_tax.id)
                    item['expense_tax_data'] = {
                        'id': str(expense_tax.id),
                        'code': expense_tax.code,
                        'title': expense_tax.title,
                        'rate': expense_tax.rate
                    }
                else:
                    item['expense_tax_id'] = None
                    item['expense_tax_data'] = {}
                    item['expense_tax_price'] = 0
            print('9. validate_payment_item_list --- ok')
            return validate_data
        except Exception as err:
            print(err)
            raise serializers.ValidationError({'payment_item_list': "Payment data is not valid."})

    @classmethod
    def validate_common(cls, validate_data):
        if 'title' in validate_data:
            if validate_data.get('title'):
                validate_data['title'] = validate_data.get('title')
            else:
                raise serializers.ValidationError({'title': "Title is not null"})
            print('10. validate_common --- ok')
        return validate_data

    @classmethod
    def validate_attachment(cls, context_user, doc_id, validate_data):
        if 'attachment' in validate_data:
            if validate_data.get('attachment'):
                if context_user and hasattr(context_user, 'employee_current_id'):
                    state, result = PaymentAttachmentFile.valid_change(
                        current_ids=validate_data.get('attachment', []),
                        employee_id=context_user.employee_current_id,
                        doc_id=doc_id
                    )
                    if state is True:
                        validate_data['attachment'] = result
                    else:
                        raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
                else:
                    raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})
            print('11. validate_attachment --- ok')
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
    def create_payment_items(cls, payment_obj, payment_item_list):
        vnd_currency = Currency.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            abbreviation='VND'
        ).first()
        if vnd_currency:
            bulk_info = []
            payment_value = 0
            for item in payment_item_list:
                if float(item['real_value']) + float(item['converted_value']) == float(item['sum_value']):
                    payment_value += item.get('expense_after_tax_price', 0)
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

            if len(bulk_info) > 0:
                PaymentCost.objects.filter(payment=payment_obj).delete()
                PaymentCost.objects.bulk_create(bulk_info)
                payment_obj.payment_value = payment_value
                payment_value_by_words = PaymentCommonFunction.read_money_vnd(payment_value).capitalize()
                if payment_value_by_words[-1] == ',':
                    payment_value_by_words = payment_value_by_words[:-1] + ' đồng'
                payment_obj.payment_value_by_words = payment_value_by_words

                opp = payment_obj.opportunity_mapped
                quotation = payment_obj.quotation_mapped
                sale_order = payment_obj.sale_order_mapped
                sale_code = sale_order.code if (
                    sale_order
                ) else quotation.code if quotation else opp.code if opp else None
                payment_obj.sale_code = sale_code

                payment_obj.save(update_fields=['payment_value', 'payment_value_by_words', 'sale_code'])
        return True

    @classmethod
    def handle_attach_file(cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="1010563f-7c94-42f9-ba99-63d5d26a1aca").first()
            if relate_app:
                state = PaymentAttachmentFile.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
        return True


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
