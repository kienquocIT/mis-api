from rest_framework import serializers
from apps.sales.cashoutflow.models import (
    Payment, PaymentCost, PaymentCostItems, PaymentCostItemsDetail, PaymentConfig,
    AdvancePaymentCost, PaymentQuotation, PaymentSaleOrder, PaymentOpportunity
)
from apps.masterdata.saledata.models import Currency
from apps.shared import AdvancePaymentMsg, ProductMsg


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
            'beneficiary',
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


def create_payment_cost_detail_items(payment_obj, payment_cost_item_list):
    expense_ap_bulk_info = []
    for payment_cost_item in payment_cost_item_list:
        for expense_ap_items in payment_cost_item.expense_items_detail_list:
            ap_item_id = expense_ap_items.get('expense_converted_id', None)
            ap_item_value = expense_ap_items.get('expense_value_converted', 0)
            if ap_item_id:
                expense_ap_bulk_info.append(
                    PaymentCostItemsDetail(
                        **expense_ap_items,
                        payment_mapped=payment_obj,
                        payment_cost_item=payment_cost_item,
                    )
                )
                ap_item_updated = AdvancePaymentCost.objects.filter(id=ap_item_id).first()
                ap_item_updated.sum_converted_value = float(ap_item_updated.sum_converted_value) + float(ap_item_value)
                ap_item_updated.save()
    PaymentCostItemsDetail.objects.filter(payment_cost_item__in=payment_cost_item_list).delete()
    PaymentCostItemsDetail.objects.bulk_create(expense_ap_bulk_info)
    return True


def create_payment_cost_items(payment_obj, payment_cost_list):
    payment_cost_bulk_info = []
    for payment_cost in payment_cost_list:
        for expense_ap_detail in payment_cost.expense_ap_detail_list:
            payment_cost_bulk_info.append(PaymentCostItems(**expense_ap_detail, payment_cost=payment_cost))
    PaymentCostItems.objects.filter(payment_cost__in=payment_cost_list).delete()
    payment_cost_item_list = PaymentCostItems.objects.bulk_create(payment_cost_bulk_info)
    create_payment_cost_detail_items(payment_obj, payment_cost_item_list)
    return True


def create_expense_items(instance, payment_expense_valid_list):
    vnd_currency = Currency.objects.filter_current(fill__tenant=True, fill__company=True, abbreviation='VND').first()
    if vnd_currency:
        bulk_info = []
        for item in payment_expense_valid_list:
            bulk_info.append(PaymentCost(**item, payment=instance, currency=vnd_currency))
        PaymentCost.objects.filter(payment=instance).delete()
        payment_cost_list = PaymentCost.objects.bulk_create(bulk_info)
        create_payment_cost_items(instance, payment_cost_list)
        return True
    return False


def create_sale_code_object(payment_obj, initial_data):
    sale_code = initial_data.get('sale_code_list', [])
    if initial_data.get('sale_code_type', None) == 0 and len(sale_code) == 1:
        sale_code_id = sale_code[0].get('sale_code_id', None)
        sale_code_detail = sale_code[0].get('sale_code_detail', None)
        if sale_code_detail == 0:
            PaymentOpportunity.objects.create(payment_mapped=payment_obj, opportunity_mapped_id=sale_code_id)
        if sale_code_detail == 1:
            PaymentQuotation.objects.create(payment_mapped=payment_obj, quotation_mapped_id=sale_code_id)
        if sale_code_detail == 2:
            PaymentSaleOrder.objects.create(payment_mapped=payment_obj, sale_order_mapped_id=sale_code_id)
    if initial_data.get('sale_code_type', None) == 3 and len(sale_code) > 0:
        so_bulk_info = []
        qo_info = []
        op_bulk_info = []
        for item in sale_code:
            sale_code_id = item.get('sale_code_id', None)
            sale_code_detail = item.get('sale_code_detail', None)
            if sale_code_detail == 0:
                so_bulk_info.append(
                    PaymentSaleOrder(payment_mapped=payment_obj, sale_order_mapped_id=sale_code_id)
                )
            if sale_code_detail == 1:
                qo_info.append(
                    PaymentQuotation(payment_mapped=payment_obj, quotation_mapped_id=sale_code_id)
                )
            if sale_code_detail == 2:
                op_bulk_info.append(
                    PaymentOpportunity(payment_mapped=payment_obj, opportunity_mapped_id=sale_code_id)
                )
        PaymentSaleOrder.objects.filter(payment_mapped=payment_obj).delete()
        PaymentSaleOrder.objects.bulk_create(so_bulk_info)
        PaymentQuotation.objects.filter(payment_mapped=payment_obj).delete()
        PaymentQuotation.objects.bulk_create(qo_info)
        PaymentOpportunity.objects.filter(payment_mapped=payment_obj).delete()
        PaymentOpportunity.objects.bulk_create(op_bulk_info)
    return True


class PaymentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Payment
        fields = (
            'title',
            'sale_code_type',
            'supplier',
            'method',
            'creator_name',
            'beneficiary',
        )

    @classmethod
    def validate_sale_code_type(cls, attrs):
        if attrs in [0, 1, 2, 3]:
            return attrs
        raise serializers.ValidationError({'Sale code type': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError({'Method': AdvancePaymentMsg.SALE_CODE_TYPE_ERROR})

    def validate(self, validate_data):
        sale_code_list = self.initial_data.get('sale_code_list', None)
        if len(sale_code_list) < 1:
            raise serializers.ValidationError({'Sale code': AdvancePaymentMsg.SALE_CODE_IS_NOT_NULL})
        if self.initial_data.get('product_valid_list', []):
            for item in self.initial_data['product_valid_list']:
                if not item.get('product_id', None):
                    raise serializers.ValidationError({'Product': ProductMsg.PRODUCT_DOES_NOT_EXIST})
        return validate_data

    def create(self, validated_data):
        if Payment.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'PAYMENT.0001'
        else:
            latest_code = Payment.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1
            new_code = 'PAYMENT.000' + str(new_code)

        payment_obj = Payment.objects.create(code=new_code, **validated_data)

        create_sale_code_object(payment_obj, self.initial_data)
        if len(self.initial_data.get('payment_expense_valid_list', [])) > 0:
            create_expense_items(payment_obj, self.initial_data.get('payment_expense_valid_list', []))
        return payment_obj


class PaymentDetailSerializer(serializers.ModelSerializer):
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    expense_items = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    beneficiary = serializers.SerializerMethodField()
    creator_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'id',
            'sale_order_mapped',
            'quotation_mapped',
            'opportunity_mapped',
            'title',
            'code',
            'creator_name',
            'beneficiary',
            'date_created',
            'method',
            'sale_code_type',
            'supplier',
            'expense_items'
        )

    @classmethod
    def get_sale_order_mapped(cls, obj):
        all_sale_order_mapped = []
        for item in obj.sale_order_mapped.all().select_related('opportunity'):
            all_sale_order_mapped.append({
                'id': str(item.id),
                'code': item.code,
                'title': item.title,
                'opportunity': {
                    'id': item.opportunity.id,
                    'code': item.opportunity.code,
                    'title': item.opportunity.title,
                    'customer': item.opportunity.customer.name,
                } if item.opportunity else {},
            })
        return all_sale_order_mapped

    @classmethod
    def get_quotation_mapped(cls, obj):
        all_quotation_mapped = []
        for item in obj.quotation_mapped.all().select_related('opportunity'):
            opportunity_obj = {}
            if item.opportunity:
                opportunity_obj = {
                    'id': item.opportunity.id,
                    'code': item.opportunity.code,
                    'title': item.opportunity.title,
                    'customer': item.opportunity.customer.name,
                }
            all_quotation_mapped.append(
                {
                    'id': str(item.id),
                    'code': item.code,
                    'title': item.title,
                    'opportunity': opportunity_obj
                }
            )
        return all_quotation_mapped

    @classmethod
    def get_opportunity_mapped(cls, obj):
        all_opportunity_mapped = []
        for item in obj.opportunity_mapped.all():
            all_opportunity_mapped.append(
                {
                    'id': str(item.id),
                    'code': item.code,
                    'title': item.title,
                    'customer': item.customer.name,
                }
            )
        return all_opportunity_mapped

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
    def get_beneficiary(cls, obj):
        return {
            'id': obj.beneficiary_id,
            'first_name': obj.beneficiary.first_name,
            'last_name': obj.beneficiary.last_name,
            'email': obj.beneficiary.email,
            'full_name': obj.beneficiary.get_full_name(2),
            'code': obj.beneficiary.code,
            'is_active': obj.beneficiary.is_active,
            'group': {
                'id': obj.beneficiary.group_id,
                'title': obj.beneficiary.group.title,
                'code': obj.beneficiary.group.code
            } if obj.beneficiary.group else {}
        } if obj.beneficiary else {}

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
    def get_expense_items(cls, obj):
        all_expense_items_mapped = []
        for item in obj.payment.all():
            all_expense_items_mapped.append({
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
                    'title': item.expense_tax.title
                } if item.expense_tax else {},
                'expense_tax_price': item.expense_tax_price,
                'expense_subtotal_price': item.expense_subtotal_price,
                'expense_after_tax_price': item.expense_after_tax_price,
                'document_number': item.document_number,
                'expense_ap_detail_list': item.expense_ap_detail_list
            })
        return all_expense_items_mapped


class PaymentCostItemsListSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()

    class Meta:
        model = PaymentCostItems
        fields = (
            'product_id',
            'payment_cost',
            'sale_code_mapped',
            'real_value',
            'converted_value',
            'sum_value',
        )

    @classmethod
    def get_product_id(cls, obj):
        return obj.payment_cost.product_id


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
