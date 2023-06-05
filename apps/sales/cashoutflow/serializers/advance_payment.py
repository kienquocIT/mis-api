from rest_framework import serializers
from apps.sales.cashoutflow.models import AdvancePayment, AdvancePaymentCost, PaymentCostItemsDetail
from apps.masterdata.saledata.models import Currency, AccountBanks
from apps.shared import AdvancePaymentMsg, AccountsMsg


class AdvancePaymentListSerializer(serializers.ModelSerializer):
    advance_payment_type = serializers.SerializerMethodField()
    to_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    remain_value = serializers.SerializerMethodField()
    advance_value = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

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
            'status',
            'to_payment',
            'return_value',
            'remain_value',
            'money_gave',
            'beneficiary',
            'sale_order_mapped',
            'quotation_mapped',
        )

    @classmethod
    def get_advance_payment_type(cls, obj):
        if obj.advance_payment_type:
            return "To Supplier"
        return "To Employee"

    @classmethod
    def get_advance_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_ap_value = sum(item.after_tax_price for item in all_items)
        return sum_ap_value

    @classmethod
    def get_to_payment(cls, obj):
        obj.to_payment = 0
        return obj.to_payment

    @classmethod
    def get_return_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_return_value = sum(item.sum_return_value for item in all_items)
        return sum_return_value

    @classmethod
    def get_remain_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_ap_value = sum(item.after_tax_price for item in all_items)
        sum_return_value = sum(item.sum_return_value for item in all_items)
        sum_payment_converted_value = sum(item.sum_converted_value for item in all_items)
        return sum_ap_value - sum_return_value - sum_payment_converted_value

    @classmethod
    def get_status(cls, obj):
        obj.status = "Approved"
        return obj.status


def create_expense_items(instance, expense_valid_list):
    vnd_currency = Currency.objects.filter_current(
        fill__tenant=True,
        fill__company=True,
        abbreviation='VND'
    ).first()
    if vnd_currency:
        bulk_info = []
        for item in expense_valid_list:
            bulk_info.append(
                AdvancePaymentCost(
                    advance_payment=instance,
                    expense_id=item.get('expense_id', None),
                    expense_unit_of_measure_id=item.get('unit_of_measure_id', None),
                    expense_quantity=item.get('quantity', None),
                    expense_unit_price=item.get('unit_price', None),
                    tax_id=item.get('tax_id', None),
                    tax_price=item.get('tax_price', None),
                    subtotal_price=item.get('subtotal_price', None),
                    after_tax_price=item.get('after_tax_price', None),
                    currency=vnd_currency,
                )
            )
        if len(bulk_info) > 0:
            AdvancePaymentCost.objects.filter(advance_payment=instance).delete()
            AdvancePaymentCost.objects.bulk_create(bulk_info)
        return True
    return False


def add_banking_accounts_information(instance, banking_accounts_list):
    bulk_info = []
    for item in banking_accounts_list:
        if item['bank_name'] and item['bank_code'] and item['bank_account_name'] and item['bank_account_number']:
            bulk_info.append(
                AccountBanks(**item, account=instance)
            )
        else:
            raise serializers.ValidationError(AccountsMsg.BANK_ACCOUNT_MISSING_VALUE)
    if len(bulk_info) > 0:
        AccountBanks.objects.filter(account=instance).delete()
        AccountBanks.objects.bulk_create(bulk_info)
    return True


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
            'beneficiary',
            'return_date',
            'money_gave'
        )

    @classmethod
    def validate_sale_code_type(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    @classmethod
    def validate_advance_payment_type(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.TYPE_ERROR)

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    def validate(self, validate_data):
        if 'sale_code' in self.initial_data:
            sale_code = self.initial_data['sale_code']
            if sale_code.get('id', None):
                if sale_code.get('type', None) == '0':
                    validate_data['sale_order_mapped_id'] = sale_code.get('id', None)
                if sale_code.get('type', None) == '1':
                    validate_data['quotation_mapped_id'] = sale_code.get('id', None)
        else:
            if self.initial_data.get('sale_code_type', None) != 2:
                raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_NOT_EXIST)
        return validate_data

    def create(self, validated_data):
        supplier = validated_data.get('supplier', None)
        if supplier:
            if self.initial_data['account_bank_information_dict'][str(supplier.id)]:
                bank_accounts_information = self.initial_data['account_bank_information_dict'][str(supplier.id)]
                supplier.bank_accounts_information = bank_accounts_information
                supplier.save()
                add_banking_accounts_information(supplier, bank_accounts_information)
        if AdvancePayment.objects.all().count() == 0:
            new_code = 'AP.CODE.0001'
        else:
            latest_code = AdvancePayment.objects.latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1  # "AP.CODE.00034" > "00034" > 34 > 35 > "AP.CODE.00035"
            new_code = 'AP.CODE.000' + str(new_code)

        advance_payment_obj = AdvancePayment.objects.create(**validated_data, code=new_code)
        if self.initial_data.get('expense_valid_list', None):
            create_expense_items(advance_payment_obj, self.initial_data.get('expense_valid_list', None))
        return advance_payment_obj


class AdvancePaymentDetailSerializer(serializers.ModelSerializer):
    expense_items = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    beneficiary = serializers.SerializerMethodField()
    converted_payment_list = serializers.SerializerMethodField()

    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
            'advance_payment_type',
            'date_created',
            'return_date',
            'money_gave',
            'sale_code_type',
            'quotation_mapped',
            'sale_order_mapped',
            'supplier',
            'method',
            'beneficiary',
            'expense_items',
            'converted_payment_list'
        )

    @classmethod
    def get_expense_items(cls, obj):
        all_item = obj.advance_payment.select_related('currency', 'expense', 'tax', 'expense_unit_of_measure').all()
        expense_items = []
        for item in all_item:
            tax_dict = None
            if item.tax:
                tax_dict = {'id': item.tax_id, 'code': item.tax.code, 'title': item.tax.title}

            expense_items.append(
                {
                    'id': item.id,
                    'expense': {
                        'id': item.expense_id,
                        'code': item.expense.code,
                        'title': item.expense.title,
                        'type': item.expense.general_information['expense_type'],
                    },
                    'tax': tax_dict,
                    'unit_price': item.expense_unit_price,
                    'subtotal_price': item.subtotal_price,
                    'after_tax_price': item.after_tax_price,
                    'expense_quantity': item.expense_quantity,
                    'expense_uom': {
                        'id': item.expense_unit_of_measure_id,
                        'code': item.expense_unit_of_measure.code,
                        'title': item.expense_unit_of_measure.title
                    },
                    'currency': {'id': item.currency_id, 'abbreviation': item.currency.abbreviation},
                    'remain_total': item.after_tax_price - item.sum_converted_value - item.sum_return_value,
                }
            )
        return expense_items

    @classmethod
    def get_sale_order_mapped(cls, obj):
        if obj.sale_order_mapped:
            return {
                'id': obj.sale_order_mapped.id,
                'code': obj.sale_order_mapped.code,
                'title': obj.sale_order_mapped.title,
                'opportunity': {
                    'id': obj.sale_order_mapped.opportunity.id,
                    'code': obj.sale_order_mapped.opportunity.code,
                    'title': obj.sale_order_mapped.opportunity.title,
                    'customer': obj.sale_order_mapped.opportunity.customer.name,
                }
            }
        return None

    @classmethod
    def get_quotation_mapped(cls, obj):
        if obj.quotation_mapped:
            return {
                'id': obj.quotation_mapped.id,
                'code': obj.quotation_mapped.code,
                'title': obj.quotation_mapped.title,
                'opportunity': {
                    'id': obj.quotation_mapped.opportunity.id,
                    'code': obj.quotation_mapped.opportunity.code,
                    'title': obj.quotation_mapped.opportunity.title,
                    'customer': obj.quotation_mapped.opportunity.customer.name,
                }
            }
        return None

    @classmethod
    def get_beneficiary(cls, obj):
        return {
            'id': obj.beneficiary.id,
            'name': obj.beneficiary.get_full_name(),
        }

    @classmethod
    def get_converted_payment_list(cls, obj):
        all_items = obj.advance_payment.all()
        all_converted_items = PaymentCostItemsDetail.objects.filter(
            expense_converted__in=all_items
        ).select_related('payment_mapped')
        converted_payment_list = []
        payment_code_list = []
        for item in all_converted_items:
            payment_code = item.payment_mapped.code
            result = None
            for converted_payment in converted_payment_list:
                if converted_payment['payment_code'] == payment_code:
                    result = converted_payment
                    break
            if result:
                if payment_code not in payment_code_list:
                    converted_payment_list.append({
                        'payment_code': payment_code,
                        'payment_title': item.payment_mapped.title,
                        'payment_value_converted': item.expense_value_converted
                    })
                    payment_code_list.append(payment_code)
            else:
                result['payment_value_converted'] = result['payment_value_converted'] + item.expense_value_converted
        return converted_payment_list


class AdvancePaymentUpdateSerializer(serializers.ModelSerializer):
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
            'beneficiary',
            'return_date',
            'money_gave'
        )

    # @classmethod
    # def validate_sale_code_type(cls, attrs):
    #     if attrs in [0, 1, 2]:
    #         return attrs
    #     raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)
    #
    # @classmethod
    # def validate_advance_payment_type(cls, attrs):
    #     if attrs in [0, 1]:
    #         return attrs
    #     raise serializers.ValidationError(AdvancePaymentMsg.TYPE_ERROR)
    #
    # @classmethod
    # def validate_method(cls, attrs):
    #     if attrs in [0, 1]:
    #         return attrs
    #     raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)
    #
    # def validate(self, validate_data):
    #     if 'sale_code' in self.initial_data:
    #         sale_code = self.initial_data['sale_code']
    #         if sale_code.get('id', None):
    #             if sale_code.get('type', None) == '0':
    #                 validate_data['sale_order_mapped_id'] = sale_code.get('id', None)
    #             if sale_code.get('type', None) == '1':
    #                 validate_data['quotation_mapped_id'] = sale_code.get('id', None)
    #     else:
    #         if self.initial_data.get('sale_code_type', None) != 2:
    #             raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_NOT_EXIST)
    #     return validate_data

    def update(self, instance, validated_data):
        # supplier = validated_data.get('supplier', None)
        # if supplier:
        #     if self.initial_data['account_bank_information_dict'][str(supplier.id)]:
        #         bank_accounts_information = self.initial_data['account_bank_information_dict'][str(supplier.id)]
        #         supplier.bank_accounts_information = bank_accounts_information
        #         supplier.save()
        #         add_banking_accounts_information(supplier, bank_accounts_information)
        #
        # if validated_data.get('sale_code_type', None) == 0:
        #     instance.sale_order_mapped = None
        #     instance.quotation_mapped = None
        # for key, value in validated_data.items():
        #     setattr(instance, key, value)
        # instance.save()

        # if self.initial_data.get('expense_valid_list', None):
        #     create_expense_items(instance, self.initial_data.get('expense_valid_list', None))
        return instance
