from rest_framework import serializers

from apps.core.process.utils import ProcessRuntimeControl
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.cashoutflow.models import (
    ReturnAdvance, ReturnAdvanceCost, AdvancePayment, AdvancePaymentCost,
)
from apps.masterdata.saledata.models import ExpenseItem
from apps.shared import (
    SaleMsg,
    AbstractDetailSerializerModel,
    AbstractCreateSerializerModel,
    AbstractListSerializerModel,
)


class ReturnAdvanceListSerializer(AbstractListSerializerModel):
    advance_payment = serializers.SerializerMethodField()
    money_received = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'system_status',
            'money_received',
            'return_total',
            'employee_inherit'
        )

    @classmethod
    def get_advance_payment(cls, obj):
        return {
            'id': obj.advance_payment.id,
            'code': obj.advance_payment.code,
            'title': obj.advance_payment.title,
            'sale_code': obj.advance_payment.sale_code,
            'opportunity': {
                'id': obj.advance_payment.opportunity_id,
                'code': obj.advance_payment.opportunity.code,
                'title': obj.advance_payment.opportunity.title
            } if obj.advance_payment.opportunity else {},
            'quotation_mapped': {
                'id': obj.advance_payment.quotation_mapped_id,
                'code': obj.advance_payment.quotation_mapped.code,
                'title': obj.advance_payment.quotation_mapped.title,
            } if obj.advance_payment.quotation_mapped else {},
            'sale_order_mapped': {
                'id': obj.advance_payment.sale_order_mapped_id,
                'code': obj.advance_payment.sale_order_mapped.code,
                'title': obj.advance_payment.sale_order_mapped.title
            } if obj.advance_payment.sale_order_mapped else {}
        } if obj.advance_payment else {}

    @classmethod
    def get_money_received(cls, obj):
        return obj.money_received

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'group': {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title,
                'code': obj.employee_inherit.group.code
            } if obj.employee_inherit.group else {}
        } if obj.employee_inherit else {}


class ReturnAdvanceCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)
    advance_payment_id = serializers.UUIDField()
    returned_list = serializers.ListField(required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=ReturnAdvance.get_app_id(),
        ) if attrs else None

    class Meta:
        model = ReturnAdvance
        fields = (
            # process
            'process',
            'process_stage_app',
            #
            'title',
            'advance_payment_id',
            'method',
            'money_received',
            'returned_list',
        )

    @classmethod
    def validate_advance_payment_id(cls, attrs):
        return ReturnAdvanceCommonFunction.validate_advance_payment(advance_payment_id=attrs)

    def validate(self, validate_data):
        advance_payment_obj = validate_data.pop('advance_payment_id')
        validate_data['advance_payment'] = advance_payment_obj
        validate_data['employee_inherit_id'] = advance_payment_obj.employee_inherit_id
        validate_data['process'] = advance_payment_obj.process

        ReturnAdvanceCommonFunction.validate_method(validate_data)
        ReturnAdvanceCommonFunction.validate_returned_list(validate_data)

        process_obj = advance_payment_obj.process
        process_stage_app_obj = advance_payment_obj.process_stage_app
        opportunity_id = advance_payment_obj.opportunity_id
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=opportunity_id)

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        returned_list = validated_data.pop('returned_list', [])
        return_advance_obj = ReturnAdvance.objects.create(**validated_data)
        ReturnAdvanceCommonFunction.common_create_return_advance_cost(returned_list, return_advance_obj)

        if return_advance_obj.process:
            ProcessRuntimeControl(process_obj=return_advance_obj.process).register_doc(
                process_stage_app_obj=return_advance_obj.process_stage_app,
                app_id=ReturnAdvance.get_app_id(),
                doc_id=return_advance_obj.id,
                doc_title=return_advance_obj.title,
                employee_created_id=return_advance_obj.employee_created_id,
                date_created=return_advance_obj.date_created,
            )

        return return_advance_obj


class ReturnAdvanceDetailSerializer(AbstractDetailSerializerModel):
    returned_list = serializers.SerializerMethodField()
    advance_payment = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()
    date_created_parsed = serializers.SerializerMethodField()

    class Meta:
        model = ReturnAdvance
        fields = (
            'id',
            'code',
            'title',
            'advance_payment',
            'employee_created',
            'employee_inherit',
            'method',
            'system_status',
            'money_received',
            'date_created_parsed',
            'returned_list',
            'return_total',
            'process',
            'process_stage_app',
        )

    @classmethod
    def get_process(cls, obj):
        return {
            'id': obj.process.id,
            'title': obj.process.title,
            'remark': obj.process.remark,
        } if obj.process else {}

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
    def get_advance_payment(cls, obj):
        return {
            'id': obj.advance_payment_id,
            'title': obj.advance_payment.title,
            'sale_code': obj.advance_payment.sale_code,
            'opportunity': {
                'id': obj.advance_payment.opportunity_id,
                'code': obj.advance_payment.opportunity.code,
                'title': obj.advance_payment.opportunity.title,
            } if obj.advance_payment.opportunity else {},
            'quotation_mapped': {
                'id': obj.advance_payment.quotation_mapped_id,
                'code': obj.advance_payment.quotation_mapped.code,
                'title': obj.advance_payment.quotation_mapped.title,
            } if obj.advance_payment.quotation_mapped else {},
            'sale_order_mapped': {
                'id': obj.advance_payment.sale_order_mapped_id,
                'code': obj.advance_payment.sale_order_mapped.code,
                'title': obj.advance_payment.sale_order_mapped.title,
            } if obj.advance_payment.sale_order_mapped else {}
        } if obj.advance_payment else {}

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'full_name': obj.employee_created.get_full_name(2),
            'code': obj.employee_created.code,
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
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'group': {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title,
                'code': obj.employee_inherit.group.code
            } if obj.employee_inherit.group else {}
        } if obj.employee_inherit else {}

    @classmethod
    def get_returned_list(cls, obj):
        list_result = []
        for item in obj.return_advance.all():
            list_result.append({
                'id': item.advance_payment_cost_id,
                'expense_name': item.expense_name,
                'expense_type': item.expense_type_data,
                'remain_total': item.remain_value,
                'return_value': item.return_value
            })
        return list_result

    @classmethod
    def get_date_created_parsed(cls, obj):
        return obj.date_created.strftime('%d/%m/%Y')


class ReturnAdvanceUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=150)
    advance_payment_id = serializers.UUIDField()
    returned_list = serializers.ListField(required=False)

    class Meta:
        model = ReturnAdvance
        fields = (
            'title',
            'advance_payment_id',
            'method',
            'money_received',
            'returned_list',
        )

    def validate(self, validate_data):
        ReturnAdvanceCommonFunction.validate_advance_payment_id(validate_data)
        ReturnAdvanceCommonFunction.validate_method(validate_data)
        ReturnAdvanceCommonFunction.validate_returned_list(validate_data)
        advance_payment_obj = AdvancePayment.objects.filter(id=validate_data.get('advance_payment_id')).first()
        if advance_payment_obj:
            validate_data['employee_inherit_id'] = advance_payment_obj.employee_inherit_id
            validate_data['process'] = advance_payment_obj.process
            print('*validate done')
            return validate_data
        raise serializers.ValidationError({'advance_payment_id': SaleMsg.AP_NOT_EXIST})


    @decorator_run_workflow
    def update(self, instance, validated_data):
        returned_list = validated_data.pop('returned_list', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        ReturnAdvanceCommonFunction.common_create_return_advance_cost(returned_list, instance)
        return instance


class ReturnAdvanceCommonFunction:
    @classmethod
    def validate_advance_payment(cls, advance_payment_id) -> AdvancePayment:
        if advance_payment_id:
            try:
                ap_obj = AdvancePayment.objects.get(id=advance_payment_id)
                if ap_obj.opportunity:
                    if ap_obj.opportunity.is_deal_close:
                        raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                return ap_obj
            except AdvancePayment.DoesNotExist:
                raise serializers.ValidationError({'advance_payment_id': SaleMsg.AP_NOT_EXIST})
        raise serializers.ValidationError({'advance_payment_id': SaleMsg.AP_NOT_EXIST})

    @classmethod
    def validate_advance_payment_id(cls, validate_data):
        if 'advance_payment_id' in validate_data:
            if validate_data.get('advance_payment_id'):
                try:
                    ap_obj = AdvancePayment.objects.get(id=validate_data.get('advance_payment_id'))
                    if ap_obj.opportunity:
                        if ap_obj.opportunity.is_deal_close:
                            raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
                    validate_data['advance_payment_id'] = str(ap_obj.id)
                except AdvancePayment.DoesNotExist:
                    raise serializers.ValidationError({'advance_payment_id': SaleMsg.AP_NOT_EXIST})
            else:
                raise serializers.ValidationError({'advance_payment_id': SaleMsg.AP_NOT_EXIST})
        print('1. validate_advance_payment_id --- ok')
        return validate_data

    @classmethod
    def validate_method(cls, validate_data):
        if validate_data['method'] in [0, 1]:
            print('2. validated_method --- ok')
            return validate_data
        raise serializers.ValidationError({'method': SaleMsg.AP_METHOD_INVALID})

    @classmethod
    def validate_returned_list(cls, validate_data):
        try:
            for item in validate_data.get('returned_list', []):
                ap_cost = AdvancePaymentCost.objects.get(id=item['advance_payment_cost_id'])
                item['advance_payment_cost_id'] = str(ap_cost.id)
                expense_type = ExpenseItem.objects.get(id=item['expense_type_id'])
                item['expense_type_id'] = str(expense_type.id)
                item['expense_type_data'] = {
                    'id': str(expense_type.id),
                    'code': expense_type.code,
                    'title': expense_type.title
                }
                if float(item.get('return_value', 0)) < 0:
                    raise serializers.ValidationError({'returned_list': "Value must be greater than 0."})
                remain_value_valid = (
                        ap_cost.expense_after_tax_price - ap_cost.sum_return_value - ap_cost.sum_converted_value
                )
                if remain_value_valid < float(item.get('return_value', 0)):
                    raise serializers.ValidationError({'returned_list': "Return value is greater than remain value."})
            print('3. validated_returned_list --- ok')
            return validate_data
        except Exception as err:
            print(err)
            raise serializers.ValidationError({'returned_list': "Returned data is not valid."})

    @classmethod
    def common_create_return_advance_cost(cls, returned_list, return_advance_obj):
        data_bulk = []
        return_total = 0
        for item in returned_list:
            data_bulk.append(ReturnAdvanceCost(return_advance=return_advance_obj, **item))
            return_total += float(item['return_value'])
        ReturnAdvanceCost.objects.filter(return_advance=return_advance_obj).delete()
        ReturnAdvanceCost.objects.bulk_create(data_bulk)
        return_advance_obj.return_total = return_total
        return_advance_obj.save(update_fields=['return_total'])
        return True


class APListForReturnSerializer(AbstractListSerializerModel):
    expense_items = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
            'expense_items',
            'supplier',
            'employee_created',
            'employee_inherit',
            'sale_code',
            'process'
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
                    'expense_type': item.expense_type_data,
                    'expense_uom_name': item.expense_uom_name,
                    'expense_quantity': item.expense_quantity,
                    'expense_unit_price': item.expense_unit_price,
                    'expense_tax': item.expense_tax_data,
                    'expense_tax_price': item.expense_tax_price,
                    'expense_subtotal_price': item.expense_subtotal_price,
                    'expense_after_tax_price': item.expense_after_tax_price,
                    'remain_total': item.expense_after_tax_price - item.sum_return_value - item.sum_converted_value
                }
            )
            order += 1
        return expense_items

    @classmethod
    def get_supplier(cls, obj):
        if obj.supplier:
            bank_accounts_mapped_list = []
            for item in obj.supplier.account_banks_mapped.all():
                bank_accounts_mapped_list.append({
                    'bank_country_id': item.country_id,
                    'bank_name': item.bank_name,
                    'bank_code': item.bank_code,
                    'bank_account_name': item.bank_account_name,
                    'bank_account_number': item.bank_account_number,
                    'bic_swift_code': item.bic_swift_code,
                    'is_default': item.is_default
                })
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
    def get_process(cls, obj):
        return {
            'id': obj.process_id,
            'title': obj.process.title,
            'remark': obj.process.remark,
        } if obj.process else {}
