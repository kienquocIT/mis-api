from rest_framework import serializers
from apps.sales.cashoutflow.models import (
    Payment, PaymentCost, PaymentCostItems, PaymentCostItemsDetail,
    AdvancePaymentCost
)
from apps.masterdata.saledata.models import Currency
from apps.shared import AdvancePaymentMsg


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


def create_payment_cost_sale_code_items(paymentcost_list):
    payment_cost_bulk_info = []
    expense_ap_bulk_info = []
    for pc_item in paymentcost_list:
        expense_ap_detail_list = pc_item.expense_ap_detail_list
        for expense_ap_detail in expense_ap_detail_list:
            payment_cost_item = PaymentCostItems(
                payment_cost=pc_item,
                sale_code_mapped=expense_ap_detail.get('sale_code_mapped', None),
                real_value=expense_ap_detail.get('real_value', 0),
                converted_value=expense_ap_detail.get('converted_value', 0),
                sum_value=expense_ap_detail.get('sum_value', 0),
            )
            payment_cost_bulk_info.append(payment_cost_item)
            for expense_ap in expense_ap_detail['converted_value_detail']:
                if expense_ap.get('id', None):
                    expense_ap_bulk_info.append(
                        PaymentCostItemsDetail(
                            payment_cost_item=payment_cost_item,
                            expense_converted_id=expense_ap['id'],
                            expense_value_converted=expense_ap.get('value', 0),
                        )
                    )
                    ap_updated = AdvancePaymentCost.objects.filter(id=expense_ap['id']).first()
                    new_converted_value = ap_updated.sum_converted_value + float(expense_ap.get('value', 0))
                    ap_updated.sum_converted_value = new_converted_value
                    ap_updated.save()

    if len(payment_cost_bulk_info) > 0:
        PaymentCostItems.objects.bulk_create(payment_cost_bulk_info)
    if len(expense_ap_bulk_info) > 0:
        PaymentCostItemsDetail.objects.bulk_create(expense_ap_bulk_info)
    return True


def create_payment_cost_detail_items(payment_cost_item_list):
    expense_ap_bulk_info = []
    for pc_item in payment_cost_item_list:
        for expense_ap in pc_item.expense_items_detail_list:
            if expense_ap.get('id', None):
                expense_ap_bulk_info.append(
                    PaymentCostItemsDetail(
                        payment_cost_item=pc_item,
                        expense_converted_id=expense_ap['id'],
                        expense_value_converted=expense_ap.get('value', 0),
                    )
                )
                ap_updated = AdvancePaymentCost.objects.filter(id=expense_ap['id']).first()
                ap_updated.sum_converted_value = ap_updated.sum_converted_value + float(expense_ap.get('value', 0))
                ap_updated.save()
    PaymentCostItemsDetail.objects.filter(payment_cost_item__in=payment_cost_item_list).delete()
    PaymentCostItemsDetail.objects.bulk_create(expense_ap_bulk_info)
    return True


def create_payment_cost_items(payment_cost_list):
    payment_cost_bulk_info = []
    for pc in payment_cost_list:
        for expense_ap_detail in pc.expense_ap_detail_list:
            payment_cost_bulk_info.append(
                PaymentCostItems(
                    payment_cost=pc,
                    sale_code_mapped=expense_ap_detail.get('sale_code_mapped', None),
                    real_value=expense_ap_detail.get('real_value', 0),
                    converted_value=expense_ap_detail.get('converted_value', 0),
                    sum_value=expense_ap_detail.get('sum_value', 0),
                    expense_items_detail_list=expense_ap_detail.get('converted_value_detail', None)
                )
            )
    PaymentCostItems.objects.filter(payment_cost__in=payment_cost_list).delete()
    payment_cost_item_list = PaymentCostItems.objects.bulk_create(payment_cost_bulk_info)
    create_payment_cost_detail_items(payment_cost_item_list)
    return True


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
                PaymentCost(
                    payment=instance,
                    expense_id=item.get('expense_id', None),
                    expense_unit_of_measure_id=item.get('unit_of_measure_id', None),
                    expense_quantity=item.get('quantity', None),
                    expense_unit_price=item.get('unit_price', 0),
                    tax_id=item.get('tax_id', None),
                    tax_price=item.get('tax_price', 0),
                    subtotal_price=item.get('subtotal_price', 0),
                    after_tax_price=item.get('after_tax_price', 0),
                    currency=vnd_currency,
                    document_number=item.get('document_number', ''),
                    expense_ap_detail_list=item.get('expense_ap_detail_list', None),
                )
            )
        PaymentCost.objects.filter(payment=instance).delete()
        payment_cost_list = PaymentCost.objects.bulk_create(bulk_info)
        create_payment_cost_items(payment_cost_list)
        return True
    return False


class PaymentCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Payment
        fields = (
            'title',
            'sale_code_mapped',
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
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    def validate(self, validate_data):
        if 'sale_code' in self.initial_data:
            validate_data['sale_code_mapped'] = self.initial_data['sale_code']
        else:
            if self.initial_data.get('sale_code_type', None) != 2:
                raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_NOT_EXIST)
        return validate_data

    def create(self, validated_data):
        if Payment.objects.all().count() == 0:
            new_code = 'AP.CODE.0001'
        else:
            latest_code = Payment.objects.latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1  # "AP.CODE.00034" > "00034" > 34 > 35 > "AP.CODE.00035"
            new_code = 'AP.CODE.000' + str(new_code)

        payment_obj = Payment.objects.create(**validated_data, code=new_code)
        if self.initial_data.get('expense_valid_list', None):
            create_expense_items(payment_obj, self.initial_data.get('expense_valid_list', None))
        return payment_obj


class PaymentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'
