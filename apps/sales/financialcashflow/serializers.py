from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.core.company.models import CompanyBankAccount
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.models import CashInflow, CashInflowItem, CashInflowItemDetail
from apps.sales.saleorder.models import SaleOrder, SaleOrderPaymentStage
from apps.shared import (
    AbstractListSerializerModel,
    AbstractCreateSerializerModel,
    AbstractDetailSerializerModel,
    CashInflowMsg
)


__all__ = [
    'CashInflowListSerializer',
    'CashInflowCreateSerializer',
    'CashInflowDetailSerializer',
    'CashInflowUpdateSerializer',
    'ARInvoiceListForCashInflowSerializer',
]


# main serializers
class CashInflowListSerializer(AbstractListSerializerModel):
    class Meta:
        model = CashInflow
        fields = (
            'id',
            'code',
            'title',
            'customer_data',
            'system_status'
        )


class CashInflowCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    no_ar_invoice_data = serializers.JSONField(default=list)
    # no_ar_invoice_data = [{
    #     'sale_order_id': uuid,
    #     'sum_balance_value': number,
    #     'sum_payment_value': number,
    #     'detail_payment': [{
    #         'so_pm_stage_id': uuid,
    #         'balance_value': number,
    #         'payment_value': number,
    #     }]
    # }]
    has_ar_invoice_data = serializers.JSONField(default=list)
    # has_ar_invoice_data = [{
    #     'ar_invoice_id': uuid,
    #     'sale_order_id': uuid,
    #     'sum_balance_value': number,
    #     'sum_payment_value': number,
    #     'discount_payment': number,
    #     'discount_value': number,
    #     'detail_payment': [{
    #         'so_pm_stage_id': uuid,
    #         'balance_value': number,
    #         'payment_value': number,
    #     }]
    # }]
    payment_method_data = serializers.JSONField(default=dict)
    # payment_method_data = {
    #     'cash_value': number,
    #     'bank_value': number,
    #     'company_bank_account_id': uuid,
    # }

    class Meta:
        model = CashInflow
        fields = (
            'title',
            'customer_id',
            'posting_date',
            'document_date',
            'description',
            'purchase_advance_value',
            # detail data
            'no_ar_invoice_data',
            'has_ar_invoice_data',
            # payment method data
            'payment_method_data',
        )

    def validate(self, validate_data):
        CashInflowCommonFunction.validate_customer_id(validate_data)
        validate_data['total_value'] = 0
        CashInflowCommonFunction.validate_no_ar_invoice_data(validate_data)
        CashInflowCommonFunction.validate_has_ar_invoice_data(validate_data)
        CashInflowCommonFunction.validate_payment_method_data(validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        no_ar_invoice_data = validated_data.pop('no_ar_invoice_data', [])
        has_ar_invoice_data = validated_data.pop('has_ar_invoice_data', [])

        if len(no_ar_invoice_data) > 0:
            validated_data['no_ar_invoice_value'] = validated_data.get('total_value', 0)
        elif len(has_ar_invoice_data) > 0:
            validated_data['has_ar_invoice_value'] = validated_data.get('total_value', 0)

        cash_inflow_obj = CashInflow.objects.create(**validated_data)
        CashInflowCommonFunction.create_cif_item(cash_inflow_obj, no_ar_invoice_data, has_ar_invoice_data)

        return cash_inflow_obj


class CashInflowDetailSerializer(AbstractDetailSerializerModel):
    no_ar_invoice_data = serializers.SerializerMethodField()
    has_ar_invoice_data = serializers.SerializerMethodField()

    class Meta:
        model = CashInflow
        fields = (
            'id',
            'code',
            'title',
            'posting_date',
            'document_date',
            'description',
            'customer_data',
            'purchase_advance_value',
            'no_ar_invoice_data',
            'has_ar_invoice_data',
            'total_value',
            'cash_value',
            'bank_value',
            'company_bank_account_data'
        )

    @classmethod
    def get_no_ar_invoice_data(cls, obj):
        no_ar_invoice_data = []
        for item in obj.cash_inflow_item_cash_inflow.filter(has_ar_invoice=False):
            no_ar_invoice_data.append({
                'id': item.id,
                'cash_inflow_data': item.cash_inflow_data,
                'has_ar_invoice': item.has_ar_invoice,
                'ar_invoice_data': item.ar_invoice_data,
                'sale_order_data': item.sale_order_data,
                'sum_balance_value': item.sum_balance_value,
                'sum_payment_value': item.sum_payment_value,
                'discount_payment': item.discount_payment,
                'detail_payment': [{
                    'id': detail.id,
                    'so_pm_stage_data': detail.so_pm_stage_data,
                    'balance_value': detail.balance_value,
                    'payment_value': detail.payment_value
                } for detail in item.cash_inflow_item_detail_cash_inflow_item.all()],
            })
        return no_ar_invoice_data

    @classmethod
    def get_has_ar_invoice_data(cls, obj):
        has_ar_invoice_data = []
        for item in obj.cash_inflow_item_cash_inflow.filter(has_ar_invoice=True):
            has_ar_invoice_data.append({
                'id': item.id,
                'cash_inflow_data': item.cash_inflow_data,
                'has_ar_invoice': item.has_ar_invoice,
                'ar_invoice_data': item.ar_invoice_data,
                'sale_order_data': item.sale_order_data,
                'sum_balance_value': item.sum_balance_value,
                'sum_payment_value': item.sum_payment_value,
                'detail_payment': [{
                    'id': detail.id,
                    'so_pm_stage_data': detail.so_pm_stage_data,
                    'balance_value': detail.balance_value,
                    'payment_value': detail.payment_value
                } for detail in item.cash_inflow_item_detail_cash_inflow_item.all()],
            })
        return has_ar_invoice_data


class CashInflowUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    no_ar_invoice_data = serializers.JSONField(default=list)
    has_ar_invoice_data = serializers.JSONField(default=list)
    payment_method_data = serializers.JSONField(default=dict)

    class Meta:
        model = CashInflow
        fields = (
            'title',
            'customer_id',
            'posting_date',
            'document_date',
            'description',
            'purchase_advance_value',
            # detail data
            'no_ar_invoice_data',
            'has_ar_invoice_data',
            # payment method data
            'payment_method_data',
        )

    def validate(self, validate_data):
        CashInflowCommonFunction.validate_customer_id(validate_data)
        validate_data['total_value'] = 0
        CashInflowCommonFunction.validate_no_ar_invoice_data(validate_data)
        CashInflowCommonFunction.validate_has_ar_invoice_data(validate_data)
        CashInflowCommonFunction.validate_payment_method_data(validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        no_ar_invoice_data = validated_data.pop('no_ar_invoice_data', [])
        has_ar_invoice_data = validated_data.pop('has_ar_invoice_data', [])

        if len(no_ar_invoice_data) > 0:
            validated_data['no_ar_invoice_value'] = validated_data.get('total_value', 0)
        elif len(has_ar_invoice_data) > 0:
            validated_data['has_ar_invoice_value'] = validated_data.get('total_value', 0)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        CashInflowCommonFunction.create_cif_item(instance, no_ar_invoice_data, has_ar_invoice_data)
        return instance


class CashInflowCommonFunction:
    @classmethod
    def validate_customer_id(cls, validate_data):
        if 'customer_id' in validate_data:
            if validate_data.get('customer_id'):
                try:
                    customer = Account.objects.get(id=validate_data.get('customer_id'))
                    if not customer.is_customer_account:
                        raise serializers.ValidationError({'customer_id': CashInflowMsg.ACCOUNT_NOT_CUSTOMER})
                    validate_data['customer_id'] = str(customer.id)
                    validate_data['customer_data'] = {
                        'id': str(customer.id),
                        'code': customer.code,
                        'name': customer.name,
                        'tax_code': customer.tax_code,
                    }
                    print('1. validate_customer_id --- ok')
                    return validate_data
                except Account.DoesNotExist:
                    raise serializers.ValidationError({'customer_id': CashInflowMsg.CUSTOMER_NOT_EXIST})
        raise serializers.ValidationError({'customer_id': CashInflowMsg.CUSTOMER_NOT_NULL})

    @staticmethod
    def common_valid_ar_invoice_data(item, validate_data):
        # check so
        sale_order = SaleOrder.objects.filter(id=item.get('sale_order_id')).first()
        if not sale_order:
            raise serializers.ValidationError({'sale_order_id': CashInflowMsg.SALE_ORDER_NOT_EXIST})
        item['sale_order_id'] = str(sale_order.id)
        item['sale_order_data'] = {
            'id': str(sale_order.id),
            'code': sale_order.code,
            'title': sale_order.title
        }

        # check detail payment
        detail_payment = item.get('detail_payment', [])
        sum_balance_value_check = 0
        sum_payment_value_check = 0
        for payment_item in detail_payment:
            payment_item_balance_value = float(payment_item.get('balance_value', 0))
            payment_item_payment_value = float(payment_item.get('payment_value', 0))

            # check so payment stage
            so_pm_stage = SaleOrderPaymentStage.objects.filter(id=payment_item.get('so_pm_stage_id')).first()
            if not so_pm_stage:
                raise serializers.ValidationError({'so_pm_stage_id': CashInflowMsg.PAYMENT_STAGE_NOT_EXIST})
            payment_item['so_pm_stage_id'] = str(so_pm_stage.id)
            payment_item['so_pm_stage_data'] = {
                'id': str(so_pm_stage.id),
                'remark': so_pm_stage.remark,
                'term_data': so_pm_stage.term_data,
                'date': str(so_pm_stage.date),
                'date_type': so_pm_stage.date_type,
                'payment_ratio': so_pm_stage.payment_ratio,
                'value_before_tax': so_pm_stage.value_before_tax,
                'issue_invoice': so_pm_stage.issue_invoice,
                'value_after_tax': so_pm_stage.value_after_tax,
                'value_total': so_pm_stage.value_total,
                'due_date': str(so_pm_stage.due_date),
                'is_ar_invoice': so_pm_stage.is_ar_invoice,
                'order': so_pm_stage.order,
            }

            # check balance value has changed ?
            approved_cash_inflow_payments = sum(
                item.payment_value for item in so_pm_stage.cash_inflow_item_detail_so_pm_stage.filter(
                    cash_inflow_item__cash_inflow__system_status=3
                )
            )
            if payment_item_balance_value != so_pm_stage.value_total - approved_cash_inflow_payments:
                raise serializers.ValidationError({'balance_value': CashInflowMsg.BALANCE_VALUE_CHANGED})

            # check payment value > balance value ?
            if payment_item_payment_value > payment_item_balance_value:
                raise serializers.ValidationError({'payment_value': CashInflowMsg.PAYMENT_VALUE_NOT_VALID})

            payment_item['balance_value'] = float(payment_item.get('balance_value', 0))
            payment_item['payment_value'] = float(payment_item.get('payment_value', 0))
            sum_balance_value_check += float(payment_item.get('balance_value', 0))
            sum_payment_value_check += float(payment_item.get('payment_value', 0))

        if float(item.get('sum_payment_value', 0)) != sum_payment_value_check:
            raise serializers.ValidationError({'sum_payment_value': CashInflowMsg.SUM_PAYMENT_VALUE_NOT_MATCH})
        item['sum_balance_value'] = float(item.get('sum_balance_value', 0))
        item['sum_payment_value'] = float(item.get('sum_payment_value', 0))
        validate_data['total_value'] = float(validate_data.get('total_value', 0)) + item['sum_payment_value']
        return True

    @classmethod
    def validate_no_ar_invoice_data(cls, validate_data):
        if 'no_ar_invoice_data' in validate_data:
            for item in validate_data.get('no_ar_invoice_data', []):
                item['has_ar_invoice'] = False
                cls.common_valid_ar_invoice_data(item, validate_data)
        print('2. validate_no_ar_invoice_data --- ok')
        return validate_data

    @classmethod
    def validate_has_ar_invoice_data(cls, validate_data):
        if 'has_ar_invoice_data' in validate_data:
            for item in validate_data.get('has_ar_invoice_data', []):
                item['has_ar_invoice'] = True
                # check ar invoice
                ar_invoice = ARInvoice.objects.filter(id=item.get('ar_invoice_id')).first()
                if not ar_invoice:
                    raise serializers.ValidationError({'ar_invoice_id': CashInflowMsg.AR_INVOICE_NOT_EXIST})
                item['ar_invoice_id'] = str(ar_invoice.id)
                item['ar_invoice_data'] = {
                    'id': str(ar_invoice.id),
                    'code': ar_invoice.code,
                    'title': ar_invoice.title,
                    'type_doc': 'AR invoice',
                    'document_date': str(ar_invoice.document_date),
                    'posting_date': str(ar_invoice.posting_date),
                    'sum_total_value': sum(item.product_subtotal_final for item in ar_invoice.ar_invoice_items.all())
                }
                cls.common_valid_ar_invoice_data(item, validate_data)
        print('3. validate_has_ar_invoice_data --- ok')
        return validate_data

    @classmethod
    def validate_payment_method_data(cls, validate_data):
        payment_method_data = validate_data.pop('payment_method_data', {})
        if all(key in payment_method_data for key in ['cash_value', 'bank_value']):
            # check cif total value == cash_value + bank_value ?
            validate_data['cash_value'] = float(payment_method_data.get('cash_value', 0))
            validate_data['bank_value'] = float(payment_method_data.get('bank_value', 0))
            validate_data['total_value'] = float(validate_data.get('total_value', 0))
            if validate_data['cash_value'] + validate_data['bank_value'] != validate_data['total_value']:
                raise serializers.ValidationError({'payment_method': CashInflowMsg.CIF_TOTAL_VALUE_NOT_MATCH})

            # check accounting obj (only text-field in this version)
            validate_data['accounting_cash_account'] = '1111'
            validate_data['accounting_bank_account'] = '1121'

            if validate_data['bank_value'] > 0:
                if 'company_bank_account_id' in payment_method_data:
                    try:
                        company_bank_account = CompanyBankAccount.objects.get(
                            id=payment_method_data.get('company_bank_account_id')
                        )
                        if not company_bank_account.is_active:
                            raise serializers.ValidationError(
                                {'company_bank_account_id': CashInflowMsg.BANK_NOT_ACTIVE}
                            )
                        validate_data['company_bank_account_id'] = str(company_bank_account.id)
                        validate_data['company_bank_account_data'] = {
                            'id': str(company_bank_account.id),
                            'country_id': str(company_bank_account.country_id),
                            'bank_name': company_bank_account.bank_name,
                            'bank_code': company_bank_account.bank_code,
                            'bank_account_name': company_bank_account.bank_account_name,
                            'bank_account_number': company_bank_account.bank_account_number,
                            'bic_swift_code': company_bank_account.bic_swift_code,
                            'is_default': company_bank_account.is_default
                        }
                    except CompanyBankAccount.DoesNotExist:
                        raise serializers.ValidationError({'company_bank_account_id': CashInflowMsg.BANK_NOT_EXIST})
                else:
                    raise serializers.ValidationError({'company_bank_account_id': CashInflowMsg.BANK_NOT_NULL})
            print('4. validate_payment_method_data --- ok')
            return validate_data
        raise serializers.ValidationError({'payment_method': CashInflowMsg.MISSING_PAYMENT_METHOD_INFO})

    @staticmethod
    def create_cif_item(cash_inflow_obj, no_ar_invoice_data, has_ar_invoice_data):
        bulk_info = []
        bulk_info_detail = []
        for item in no_ar_invoice_data + has_ar_invoice_data:
            detail_payment = item.pop('detail_payment', [])
            cif_item_obj = CashInflowItem(
                cash_inflow=cash_inflow_obj,
                cash_inflow_data={
                    'id': str(cash_inflow_obj.id),
                    'code': cash_inflow_obj.code,
                    'title': cash_inflow_obj.title
                } if cash_inflow_obj else {},
                **item
            )
            bulk_info.append(cif_item_obj)
            for detail in detail_payment:
                bulk_info_detail.append(CashInflowItemDetail(
                    cash_inflow_item=cif_item_obj,
                    **detail
                ))
        cash_inflow_obj.cash_inflow_item_cash_inflow.all().delete()
        CashInflowItem.objects.bulk_create(bulk_info)
        CashInflowItemDetail.objects.bulk_create(bulk_info_detail)
        print('* create_cif_item --- ok')
        return True


# related serializers
class ARInvoiceListForCashInflowSerializer(serializers.ModelSerializer):
    customer_mapped = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    payment_value = serializers.SerializerMethodField()
    sale_order_data = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'document_date',
            'customer_mapped',
            'document_type',
            'total',
            'payment_value',
            'sale_order_data'
        )

    @classmethod
    def get_customer_mapped(cls, obj):
        return {
            'id': obj.customer_mapped_id,
            'code': obj.customer_mapped.code,
            'name': obj.customer_mapped.name,
            'tax_code': obj.customer_mapped.tax_code
        } if obj.customer_mapped else {}

    @classmethod
    def get_document_type(cls, obj):
        return _('AR Invoice') if obj else ''

    @classmethod
    def get_total(cls, obj):
        total = sum(item.product_subtotal_final for item in obj.ar_invoice_items.all())
        return total

    @classmethod
    def get_payment_value(cls, obj):
        payment_value = sum(item.sum_payment_value for item in obj.cash_inflow_item_ar_invoice.filter(
            cash_inflow__system_status=3
        ))
        return payment_value

    @classmethod
    def get_sale_order_data(cls, obj):
        return {
            'id': obj.sale_order_mapped_id,
            'code': obj.sale_order_mapped.code,
            'title': obj.sale_order_mapped.title,
            'payment_term': [{
                'id': item.id,
                'so_id': obj.sale_order_mapped_id,
                'so_code': obj.sale_order_mapped.code,
                'remark': item.remark,
                'term_data': item.term_data,
                'date': item.date,
                'date_type': item.date_type,
                'payment_ratio': item.payment_ratio,
                'value_before_tax': item.value_before_tax,
                'issue_invoice': item.issue_invoice,
                'value_after_tax': item.value_after_tax,
                'value_total': item.value_total,
                'value_payment': sum(
                    item.payment_value for item in item.cash_inflow_item_detail_so_pm_stage.filter(
                        cash_inflow_item__cash_inflow__system_status=3
                    )
                ),
                'due_date': item.due_date,
                'is_ar_invoice': item.is_ar_invoice,
                'order': item.order
            } for item in obj.sale_order_mapped.payment_stage_sale_order.all()],
        } if obj.sale_order_mapped else {}
