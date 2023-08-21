from rest_framework import serializers
from apps.sales.cashoutflow.models import (
    AdvancePayment,
    AdvancePaymentCost,
    PaymentCostItemsDetail,
)
from apps.masterdata.saledata.models import Currency, AccountBanks
from apps.shared import AdvancePaymentMsg, AccountsMsg, ProductMsg


class AdvancePaymentListSerializer(serializers.ModelSerializer):
    advance_payment_type = serializers.SerializerMethodField()
    advance_value = serializers.SerializerMethodField()
    to_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    remain_value = serializers.SerializerMethodField()
    product_items = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
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
            'status',
            'advance_value',
            'to_payment',
            'return_value',
            'remain_value',
            'money_gave',
            'beneficiary',
            'sale_order_mapped',
            'quotation_mapped',
            'opportunity_mapped',
            'product_items',
            'opportunity_id',
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
                    'opportunity_id': obj.sale_order_mapped.opportunity_id,
                    'opportunity_code': obj.sale_order_mapped.opportunity.is_deal_close,
                    'is_close': is_close
                }
            return {
                'id': obj.sale_order_mapped_id,
                'opportunity_id': None,
                'opportunity_code': None,
                'is_close': is_close
            }
        return None

    @classmethod
    def get_quotation_mapped(cls, obj):
        if obj.quotation_mapped:
            is_close = False
            if obj.quotation_mapped.opportunity:
                if obj.quotation_mapped.opportunity.is_close_lost or obj.quotation_mapped.opportunity.is_deal_close:
                    is_close = True
                return {
                    'id': obj.quotation_mapped_id,
                    'opportunity_id': obj.quotation_mapped.opportunity_id,
                    'opportunity_code': obj.quotation_mapped.opportunity.code,
                    'is_close': is_close,
                }
            return {
                'id': obj.quotation_mapped_id,
                'opportunity_id': None,
                'opportunity_code': None,
                'is_close': is_close,
            }
        return None

    @classmethod
    def get_opportunity_mapped(cls, obj):
        if obj.opportunity_mapped:
            is_close = False
            if obj.opportunity_mapped.is_close_lost or obj.opportunity_mapped.is_deal_close:
                is_close = True
            return {
                'id': obj.opportunity_mapped_id,
                # 'code': obj.opportunity_mapped.code,
                'is_close': is_close
            }
        return None

    @classmethod
    def get_product_items(cls, obj):
        all_item = obj.advance_payment.all()
        product_items = []
        for item in all_item:
            tax_dict = None
            if item.tax:
                tax_dict = {'id': item.tax_id, 'code': item.tax.code, 'title': item.tax.title}

            product_obj = {}
            if item.product_id:
                product_obj = {
                    'id': item.product_id,
                    'code': item.product.code,
                    'title': item.product.title,
                    'type': item.product.general_information['product_type'],
                }

            product_items.append(
                {
                    'id': item.id,
                    'product': product_obj,
                    'tax': tax_dict,
                    'product_quantity': item.product_quantity,
                    'product_uom': {
                        'id': item.product_unit_of_measure_id,
                        'code': item.product_unit_of_measure.code,
                        'title': item.product_unit_of_measure.title
                    },
                    'currency': {'id': item.currency_id, 'abbreviation': item.currency.abbreviation},
                    'unit_price': item.product_unit_price,
                    'subtotal_price': item.subtotal_price,
                    'after_tax_price': item.after_tax_price,
                    'returned_total': item.sum_return_value,
                    'to_payment_total': item.sum_converted_value,
                    'remain_total': item.after_tax_price - item.sum_return_value - item.sum_converted_value,
                }
            )
        return product_items

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
        sum_ap_value = sum(item.after_tax_price for item in all_items)
        sum_return_value = sum(item.sum_return_value for item in all_items)
        sum_payment_converted_value = sum(item.sum_converted_value for item in all_items)
        return sum_ap_value - sum_return_value - sum_payment_converted_value

    @classmethod
    def get_status(cls, obj):
        obj.status = "Approved"
        return obj.status

    @classmethod
    def get_opportunity_id(cls, obj):
        if obj.opportunity_mapped:
            return obj.opportunity_mapped_id
        if obj.quotation_mapped:
            return obj.quotation_mapped.opportunity_id
        if obj.sale_order_mapped:
            return obj.sale_order_mapped.opportunity_id
        return None


def create_product_items(instance, product_valid_list):
    vnd_currency = Currency.objects.filter_current(
        fill__tenant=True,
        fill__company=True,
        abbreviation='VND'
    ).first()
    if vnd_currency:
        bulk_info = []
        for item in product_valid_list:
            bulk_info.append(
                AdvancePaymentCost(
                    advance_payment=instance,
                    product_id=item.get('product_id', None),
                    product_unit_of_measure_id=item.get('unit_of_measure_id', None),
                    product_quantity=item.get('quantity', None),
                    product_unit_price=item.get('unit_price', None),
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
            raise serializers.ValidationError({'Bank information': AccountsMsg.BANK_ACCOUNT_MISSING_VALUE})
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
        if self.initial_data.get('sale_code_type', None) != 2:
            if 'sale_code' in self.initial_data:
                sale_code = self.initial_data['sale_code']
                if sale_code.get('id', None):
                    if sale_code.get('type', None) == '0':
                        validate_data['sale_order_mapped_id'] = sale_code.get('id', None)
                    if sale_code.get('type', None) == '1':
                        validate_data['quotation_mapped_id'] = sale_code.get('id', None)
                    if sale_code.get('type', None) == '2':
                        validate_data['opportunity_mapped_id'] = sale_code.get('id', None)
            else:
                raise serializers.ValidationError({'Sale code': AdvancePaymentMsg.SALE_CODE_IS_NOT_NULL})

        if self.initial_data.get('product_valid_list', []):
            for item in self.initial_data['product_valid_list']:
                if not item.get('product_id', None):
                    raise serializers.ValidationError({'Product': ProductMsg.PRODUCT_DOES_NOT_EXIST})
        return validate_data

    def create(self, validated_data):
        supplier = validated_data.get('supplier', None)
        if supplier:
            if self.initial_data['account_bank_information_dict'][str(supplier.id)]:
                bank_accounts_information = self.initial_data['account_bank_information_dict'][str(supplier.id)]
                supplier.bank_accounts_information = bank_accounts_information
                supplier.save()
                add_banking_accounts_information(supplier, bank_accounts_information)
        if AdvancePayment.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'AP.CODE.0001'
        else:
            latest_code = AdvancePayment.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1  # "AP.CODE.00034" > "00034" > 34 > 35 > "AP.CODE.00035"
            new_code = 'AP.CODE.000' + str(new_code)

        advance_payment_obj = AdvancePayment.objects.create(**validated_data, code=new_code)
        if self.initial_data.get('product_valid_list', []):
            create_product_items(advance_payment_obj, self.initial_data.get('product_valid_list', []))
        return advance_payment_obj


class AdvancePaymentDetailSerializer(serializers.ModelSerializer):
    product_items = serializers.SerializerMethodField()
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    beneficiary = serializers.SerializerMethodField()
    to_payment = serializers.SerializerMethodField()
    return_value = serializers.SerializerMethodField()
    remain_value = serializers.SerializerMethodField()
    advance_value = serializers.SerializerMethodField()
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
            'opportunity_mapped',
            'supplier',
            'method',
            'beneficiary',
            'product_items',
            'advance_value',
            'to_payment',
            'return_value',
            'remain_value',
            'converted_payment_list'
        )

    @classmethod
    def get_product_items(cls, obj):
        all_item = obj.advance_payment.all()
        product_items = []
        for item in all_item:
            tax_dict = None
            if item.tax:
                tax_dict = {'id': item.tax_id, 'code': item.tax.code, 'title': item.tax.title}
            product_items.append(
                {
                    'id': item.id,
                    'product': {
                        'id': item.product_id,
                        'code': item.product.code,
                        'title': item.product.title,
                        'type': item.product.general_information['product_type'],
                    },
                    'tax': tax_dict,
                    'product_quantity': item.product_quantity,
                    'product_uom': {
                        'id': item.product_unit_of_measure_id,
                        'code': item.product_unit_of_measure.code,
                        'title': item.product_unit_of_measure.title
                    },
                    'currency': {'id': item.currency_id, 'abbreviation': item.currency.abbreviation},
                    'unit_price': item.product_unit_price,
                    'subtotal_price': item.subtotal_price,
                    'after_tax_price': item.after_tax_price,
                    'returned_total': item.sum_return_value,
                    'to_payment_total': item.sum_converted_value,
                    'remain_total': item.after_tax_price - item.sum_return_value - item.sum_converted_value,
                }
            )
        return product_items

    @classmethod
    def get_sale_order_mapped(cls, obj):
        if obj.sale_order_mapped:
            opportunity_obj = {}
            if obj.sale_order_mapped.opportunity:
                opportunity_obj = {
                    'id': obj.sale_order_mapped.opportunity.id,
                    'code': obj.sale_order_mapped.opportunity.code,
                    'title': obj.sale_order_mapped.opportunity.title,
                    'customer': obj.sale_order_mapped.opportunity.customer.name,
                }
            return [{
                'id': obj.sale_order_mapped.id,
                'code': obj.sale_order_mapped.code,
                'title': obj.sale_order_mapped.title,
                'opportunity': opportunity_obj
            }]
        return []

    @classmethod
    def get_quotation_mapped(cls, obj):
        if obj.quotation_mapped:
            opportunity_obj = {}
            if obj.quotation_mapped.opportunity:
                opportunity_obj = {
                    'id': obj.quotation_mapped.opportunity.id,
                    'code': obj.quotation_mapped.opportunity.code,
                    'title': obj.quotation_mapped.opportunity.title,
                    'customer': obj.quotation_mapped.opportunity.customer.name,
                }
            return [{
                'id': obj.quotation_mapped.id,
                'code': obj.quotation_mapped.code,
                'title': obj.quotation_mapped.title,
                'opportunity': opportunity_obj
            }]
        return []

    @classmethod
    def get_opportunity_mapped(cls, obj):
        if obj.opportunity_mapped:
            return [{
                'id': obj.opportunity_mapped_id,
                'code': obj.opportunity_mapped.code,
                'title': obj.opportunity_mapped.title,
                'customer': obj.opportunity_mapped.customer.name,
            }]
        return []

    @classmethod
    def get_beneficiary(cls, obj):
        return {
            'id': obj.beneficiary.id,
            'name': obj.beneficiary.get_full_name(),
        }

    @classmethod
    def get_advance_value(cls, obj):
        all_items = obj.advance_payment.all()
        sum_ap_value = sum(item.after_tax_price for item in all_items)
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
        sum_ap_value = sum(item.after_tax_price for item in all_items)
        sum_return_value = sum(item.sum_return_value for item in all_items)
        sum_payment_converted_value = sum(item.sum_converted_value for item in all_items)
        return sum_ap_value - sum_return_value - sum_payment_converted_value

    @classmethod
    def get_converted_payment_list(cls, obj):
        all_items = obj.advance_payment.all()
        all_converted_items = PaymentCostItemsDetail.objects.filter(
            product_converted__in=all_items
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
            if not result:
                if payment_code not in payment_code_list:
                    converted_payment_list.append({
                        'payment_code': payment_code,
                        'payment_title': item.payment_mapped.title,
                        'payment_value_converted': item.product_value_converted
                    })
                    payment_code_list.append(payment_code)
            else:
                result['payment_value_converted'] = result['payment_value_converted'] + item.product_value_converted
        return converted_payment_list


class AdvancePaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancePayment
        fields = (
            'money_gave',
        )

    def update(self, instance, validated_data):
        instance.money_gave = validated_data.get('money_gave', None)
        instance.save()
        return instance
