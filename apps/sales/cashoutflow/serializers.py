from rest_framework import serializers
from apps.sales.cashoutflow.models import AdvancePayment, AdvancePaymentCost
from apps.masterdata.saledata.models import Currency, Account, AccountBanks
from apps.shared import AdvancePaymentMsg


class AdvancePaymentListSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
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
            'type',
            'date_created',
            'return_date',
            'advance_value',
            'status',
            'to_payment',
            'return_value',
            'remain_value',
            'money_gave'
        )

    @classmethod
    def get_type(cls, obj):
        if obj.type:
            return "To Supplier"
        return "To Employee"

    @classmethod
    def get_advance_value(cls, obj):
        all_cost = AdvancePaymentCost.objects.filter(advance_payment=obj).values_list('after_tax_price', flat=False)
        obj.advance_value = sum(price[0] for price in all_cost)
        return obj.advance_value

    @classmethod
    def get_to_payment(cls, obj):
        obj.to_payment = 0
        return obj.to_payment

    @classmethod
    def get_return_value(cls, obj):
        obj.return_value = 0
        return obj.return_value

    @classmethod
    def get_remain_value(cls, obj):
        all_cost = AdvancePaymentCost.objects.filter(advance_payment=obj).values_list('after_tax_price', flat=False)
        obj.remain_value = sum(price[0] for price in all_cost)
        return obj.remain_value

    @classmethod
    def get_status(cls, obj):
        obj.status = 'Approved'
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
            AdvancePaymentCost.objects.bulk_create(bulk_info)
        return True
    return False


def add_banking_accounts_information(instance, banking_accounts_list):
    bulk_info = []
    for item in banking_accounts_list:
        bulk_info.append(
            AccountBanks(**item, account_id=instance)
        )
    if len(bulk_info) > 0:
        AccountBanks.objects.filter(account_id=instance).delete()
        AccountBanks.objects.bulk_create(bulk_info)
    return True


class AdvancePaymentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AdvancePayment
        fields = (
            'title',
            'sale_code_type',
            'type',
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
    def validate_type(cls, attrs):
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
                return validate_data
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_NOT_EXIST)

    def create(self, validated_data):
        supplier_id = validated_data.get('supplier', None)
        if supplier_id:
            if self.initial_data['account_bank_information_dict'][str(supplier_id)]:
                bank_accounts_information = self.initial_data['account_bank_information_dict'][str(supplier_id)]
                Account.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    id=supplier_id
                ).update(bank_accounts_information=bank_accounts_information)
                add_banking_accounts_information(str(supplier_id), bank_accounts_information)
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
    class Meta:
        model = AdvancePayment
        fields = (
            'id',
            'title',
            'code',
        )
