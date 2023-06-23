from rest_framework import serializers
from apps.sales.cashoutflow.models import (
    Payment, PaymentCost, PaymentCostItems, PaymentCostItemsDetail,
    AdvancePaymentCost, PaymentQuotation, PaymentSaleOrder, PaymentOpportunity
)
from apps.masterdata.saledata.models import Currency
from apps.shared import AdvancePaymentMsg


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
        sum_payment_value = sum(item.after_tax_price for item in all_items)
        return sum_payment_value

    @classmethod
    def get_return_value_list(cls, obj):
        obj.return_value_list = {}
        return obj.return_value_list

    @classmethod
    def get_payment_value(cls, obj):
        all_items = obj.payment.all()
        sum_payment_value = sum(item.after_tax_price for item in all_items)
        return sum_payment_value


def create_payment_cost_detail_items(payment_obj, payment_cost_item_list):
    expense_ap_bulk_info = []
    for payment_cost_item in payment_cost_item_list:
        for expense_ap in payment_cost_item.expense_items_detail_list:
            if expense_ap.get('id', None):
                expense_ap_bulk_info.append(
                    PaymentCostItemsDetail(
                        payment_cost_item=payment_cost_item,
                        payment_mapped=payment_obj,
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


def create_payment_cost_items(payment_obj, payment_cost_list):
    payment_cost_bulk_info = []
    for payment_cost in payment_cost_list:
        for expense_ap_detail in payment_cost.expense_ap_detail_list:
            payment_cost_bulk_info.append(
                PaymentCostItems(
                    payment_cost=payment_cost,
                    sale_code_mapped=expense_ap_detail.get('sale_code_mapped', None),
                    real_value=expense_ap_detail.get('real_value', 0),
                    converted_value=expense_ap_detail.get('converted_value', 0),
                    sum_value=expense_ap_detail.get('sum_value', 0),
                    expense_items_detail_list=expense_ap_detail.get('converted_value_detail', None)
                )
            )
            # ap_updated = AdvancePaymentCost.objects.filter(id=expense_ap['id']).first()
            # ap_updated.sum_converted_value = ap_updated.sum_converted_value + float(expense_ap.get('value', 0))
            # ap_updated.save()
    PaymentCostItems.objects.filter(payment_cost__in=payment_cost_list).delete()
    payment_cost_item_list = PaymentCostItems.objects.bulk_create(payment_cost_bulk_info)
    create_payment_cost_detail_items(payment_obj, payment_cost_item_list)
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
        create_payment_cost_items(instance, payment_cost_list)
        return True
    return False


def create_sale_code_object(payment_obj, initial_data):
    if initial_data.get('sale_code_type', None) == 0:
        sale_code_id = initial_data.get('sale_code', None)
        if sale_code_id:
            if initial_data.get('sale_code_detail', None) == 0:
                PaymentSaleOrder.objects.create(payment_mapped=payment_obj, sale_order_mapped_id=sale_code_id)
            if initial_data.get('sale_code_detail', None) == 1:
                PaymentQuotation.objects.create(payment_mapped=payment_obj, quotation_mapped_id=sale_code_id)
            if initial_data.get('sale_code_detail', None) == 2:
                PaymentOpportunity.objects.create(payment_mapped=payment_obj, opportunity_mapped_id=sale_code_id)
    if initial_data.get('sale_code_type', None) == 3:
        sale_order_bulk_info = []
        for item in initial_data.get('sale_order_selected_list', []):
            sale_order_bulk_info.append(PaymentSaleOrder(payment_mapped=payment_obj, sale_order_mapped_id=item))
        PaymentSaleOrder.objects.bulk_create(sale_order_bulk_info)

        payment_quotation_bulk_info = []
        for item in initial_data.get('quotation_selected_list', []):
            payment_quotation_bulk_info.append(PaymentQuotation(payment_mapped=payment_obj, quotation_mapped_id=item))
        PaymentQuotation.objects.bulk_create(payment_quotation_bulk_info)

        opportunity_bulk_info = []
        for item in initial_data.get('opportunity_selected_list', []):
            opportunity_bulk_info.append(PaymentOpportunity(payment_mapped=payment_obj, opportunity_mapped_id=item))
        PaymentOpportunity.objects.bulk_create(opportunity_bulk_info)
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
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    @classmethod
    def validate_method(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError(AdvancePaymentMsg.SALE_CODE_TYPE_ERROR)

    def create(self, validated_data):
        if Payment.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'PAYMENT.CODE.0001'
        else:
            latest_code = Payment.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1
            new_code = 'PAYMENT.CODE.000' + str(new_code)

        payment_obj = Payment.objects.create(code=new_code, **validated_data)

        create_sale_code_object(payment_obj, self.initial_data)
        if self.initial_data.get('expense_valid_list', None):
            create_expense_items(payment_obj, self.initial_data.get('expense_valid_list', None))
        return payment_obj


class PaymentDetailSerializer(serializers.ModelSerializer):
    sale_order_mapped = serializers.SerializerMethodField()
    quotation_mapped = serializers.SerializerMethodField()
    opportunity_mapped = serializers.SerializerMethodField()
    expense_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
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
            'expense_mapped'
        )

    @classmethod
    def get_sale_order_mapped(cls, obj):
        all_sale_order_mapped = []
        for item in obj.sale_order_mapped.all().select_related('opportunity'):
            opportunity_obj = {}
            if item.opportunity:
                opportunity_obj = {
                    'id': item.opportunity.id,
                    'code': item.opportunity.code,
                    'title': item.opportunity.title,
                    'customer': item.opportunity.customer.name,
                }
            all_sale_order_mapped.append({
                'id': str(item.id),
                'code': item.code,
                'title': item.title,
                'opportunity': opportunity_obj
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
                    'opportunity': {
                        'id': str(item.id), 'code': item.code, 'title': item.title
                    }
                }
            )
        return all_opportunity_mapped

    @classmethod
    def get_expense_mapped(cls, obj):
        all_expense_mapped = []
        for item in obj.payment.all():
            tax_obj = None
            if item.tax:
                tax_obj = {'id': item.tax_id, 'code': item.tax.code, 'title': item.tax.title}
            all_expense_mapped.append({
                'id': item.id,
                'expense': {
                    'id': item.expense_id,
                    'code': item.expense.code,
                    'title': item.expense.title
                },
                'expense_unit_of_measure': {
                    'id': item.expense_unit_of_measure_id,
                    'code': item.expense_unit_of_measure.code,
                    'title': item.expense_unit_of_measure.title
                },
                'expense_quantity': item.expense_quantity,
                'expense_unit_price': item.expense_unit_price,
                'tax': tax_obj,
                'subtotal_price': item.subtotal_price,
                'after_tax_price': item.after_tax_price,
                'document_number': item.document_number,
                'expense_ap_detail_list': item.expense_ap_detail_list
            })
        return all_expense_mapped


class PaymentCostItemsListSerializer(serializers.ModelSerializer):
    expense_id = serializers.SerializerMethodField()

    class Meta:
        model = PaymentCostItems
        fields = (
            'expense_id',
            'payment_cost',
            'sale_code_mapped',
            'real_value',
            'converted_value',
            'sum_value',
        )

    @classmethod
    def get_expense_id(cls, obj):
        return obj.payment_cost.expense_id
