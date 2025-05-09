from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, BankAccount
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.models import CashInflow, CashInflowItem, CashInflowItemDetail
from apps.sales.saleorder.models import SaleOrderPaymentStage
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
    'CustomerAdvanceForCashInflowSerializer',
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
            'total_value',
            'date_created',
            'system_status'
        )


class CashInflowCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cash_in_customer_advance_data = serializers.JSONField(default=list)
    # cash_in_customer_advance_data = [{
    #     'sale_order_id': uuid,
    #     'sum_balance_value': number,
    #     'sum_payment_value': number,
    #     'detail_payment': [{
    #         'so_pm_stage_id': uuid,
    #         'balance_value': number,
    #         'payment_value': number,
    #     }]
    # }]
    cash_in_ar_invoice_data = serializers.JSONField(default=list)
    # cash_in_ar_invoice_data = [{
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
            'cash_in_customer_advance_data',
            'cash_in_ar_invoice_data',
            # payment method data
            'payment_method_data',
        )

    def validate(self, validate_data):
        CashInflowCommonFunction.validate_customer_id(validate_data)
        validate_data['total_value'] = float(validate_data.get('purchase_advance_value', 0))
        CashInflowCommonFunction.validate_cash_in_customer_advance_data(validate_data)
        CashInflowCommonFunction.validate_cash_in_ar_invoice_data(validate_data)
        CashInflowCommonFunction.validate_payment_method_data(validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        cash_in_customer_advance_data = validated_data.pop('cash_in_customer_advance_data', [])
        cash_in_ar_invoice_data = validated_data.pop('cash_in_ar_invoice_data', [])

        if len(cash_in_customer_advance_data) > 0:
            validated_data['no_ar_invoice_value'] = validated_data.get('total_value', 0)
        elif len(cash_in_ar_invoice_data) > 0:
            validated_data['has_ar_invoice_value'] = validated_data.get('total_value', 0)

        cash_inflow_obj = CashInflow.objects.create(**validated_data)
        CashInflowCommonFunction.create_cif_item(
            cash_inflow_obj, cash_in_customer_advance_data, cash_in_ar_invoice_data
        )

        return cash_inflow_obj


class CashInflowDetailSerializer(AbstractDetailSerializerModel):
    cash_in_customer_advance_data = serializers.SerializerMethodField()
    cash_in_ar_invoice_data = serializers.SerializerMethodField()

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
            'cash_in_customer_advance_data',
            'cash_in_ar_invoice_data',
            'total_value',
            'cash_value',
            'bank_value',
            'company_bank_account_data'
        )

    @classmethod
    def get_cash_in_customer_advance_data(cls, obj):
        cash_in_customer_advance_data = []
        for item in obj.cash_inflow_item_cash_inflow.filter(has_ar_invoice=False):
            cash_in_customer_advance_data.append({
                'id': item.id,
                'cash_inflow_data': item.cash_inflow_data,
                'sale_order_stage_data': item.sale_order_stage_data,
                'sale_order_data': item.sale_order_data,
                'sum_balance_value': item.sum_balance_value,
                'sum_payment_value': item.sum_payment_value,
            })
        return cash_in_customer_advance_data

    @classmethod
    def get_cash_in_ar_invoice_data(cls, obj):
        cash_in_ar_invoice_data = []
        for item in obj.cash_inflow_item_cash_inflow.filter(has_ar_invoice=True):
            cash_in_ar_invoice_data.append({
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
        return cash_in_ar_invoice_data


class CashInflowUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cash_in_customer_advance_data = serializers.JSONField(default=list)
    cash_in_ar_invoice_data = serializers.JSONField(default=list)
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
            'cash_in_customer_advance_data',
            'cash_in_ar_invoice_data',
            # payment method data
            'payment_method_data',
        )

    def validate(self, validate_data):
        CashInflowCommonFunction.validate_customer_id(validate_data)
        validate_data['total_value'] = float(validate_data.get('purchase_advance_value', 0))
        CashInflowCommonFunction.validate_cash_in_customer_advance_data(validate_data)
        CashInflowCommonFunction.validate_cash_in_ar_invoice_data(validate_data)
        CashInflowCommonFunction.validate_payment_method_data(validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        cash_in_customer_advance_data = validated_data.pop('cash_in_customer_advance_data', [])
        cash_in_ar_invoice_data = validated_data.pop('cash_in_ar_invoice_data', [])

        if len(cash_in_customer_advance_data) > 0:
            validated_data['no_ar_invoice_value'] = validated_data.get('total_value', 0)
        elif len(cash_in_ar_invoice_data) > 0:
            validated_data['has_ar_invoice_value'] = validated_data.get('total_value', 0)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        CashInflowCommonFunction.create_cif_item(instance, cash_in_customer_advance_data, cash_in_ar_invoice_data)
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
    def common_valid_cash_in_ar_invoice_data(item):
        # check so
        ar_invoice_obj = ARInvoice.objects.filter(id=item.get('ar_invoice_id')).first()
        if not ar_invoice_obj:
            raise serializers.ValidationError({'ar_invoice_id': CashInflowMsg.AR_INVOICE_NOT_EXIST})
        if ar_invoice_obj.sale_order_mapped:
            item['sale_order_id'] = str(ar_invoice_obj.sale_order_mapped_id)
            item['sale_order_data'] = {
                'id': str(ar_invoice_obj.sale_order_mapped_id),
                'code': ar_invoice_obj.sale_order_mapped.code,
                'title': ar_invoice_obj.sale_order_mapped.title
            }
        else:
            raise serializers.ValidationError({'sale_order_id': CashInflowMsg.SALE_ORDER_NOT_EXIST})

        for row in item.get('detail_payment', []):
            sale_order_stage = SaleOrderPaymentStage.objects.filter(id=row.get('so_pm_stage_id')).first()
            if not sale_order_stage:
                raise serializers.ValidationError({'so_pm_stage_id': CashInflowMsg.SALE_ORDER_STAGE_NOT_EXIST})
            row['so_pm_stage_data'] = {
                'id': str(sale_order_stage.id),
                'remark': sale_order_stage.remark,
                'term_data': sale_order_stage.term_data,
                'date': str(sale_order_stage.date),
                'date_type': sale_order_stage.date_type,
                'ratio': sale_order_stage.ratio,
                'value_before_tax': sale_order_stage.value_before_tax,
                'invoice': sale_order_stage.invoice,
                'invoice_data': sale_order_stage.invoice_data,
                'value_total': sale_order_stage.value_total,
                'due_date': str(sale_order_stage.due_date),
                'is_ar_invoice': sale_order_stage.is_ar_invoice,
                'order': sale_order_stage.order,
            }

        item['sum_balance_value'] = float(item.get('sum_balance_value', 0))
        item['sum_payment_value'] = float(item.get('sum_payment_value', 0))
        return True

    @staticmethod
    def common_valid_cash_in_customer_advance_data(item):
        # check so
        sale_order_stage = SaleOrderPaymentStage.objects.filter(id=item.get('sale_order_stage_id')).first()
        if not sale_order_stage:
            raise serializers.ValidationError({'sale_order_stage_id': CashInflowMsg.SALE_ORDER_STAGE_NOT_EXIST})
        item['sale_order_stage_id'] = str(sale_order_stage.id)
        item['sale_order_stage_data'] = {
            'id': str(sale_order_stage.id),
            'remark': sale_order_stage.remark,
            'term_data': sale_order_stage.term_data,
            'date': str(sale_order_stage.date),
            'date_type': sale_order_stage.date_type,
            'ratio': sale_order_stage.ratio,
            'value_before_tax': sale_order_stage.value_before_tax,
            'invoice': sale_order_stage.invoice,
            'invoice_data': sale_order_stage.invoice_data,
            'value_total': sale_order_stage.value_total,
            'due_date': str(sale_order_stage.due_date),
            'is_ar_invoice': sale_order_stage.is_ar_invoice,
            'order': sale_order_stage.order,
        }
        if sale_order_stage.sale_order:
            item['sale_order_id'] = str(sale_order_stage.sale_order_id)
            item['sale_order_data'] = {
                'id': str(sale_order_stage.sale_order_id),
                'code': sale_order_stage.sale_order.code,
                'title': sale_order_stage.sale_order.title
            }
        else:
            raise serializers.ValidationError({'sale_order_id': CashInflowMsg.SALE_ORDER_NOT_EXIST})

        item['sum_balance_value'] = float(item.get('sum_balance_value', 0))
        item['sum_payment_value'] = float(item.get('sum_payment_value', 0))
        return True

    @classmethod
    def validate_cash_in_customer_advance_data(cls, validate_data):
        if 'cash_in_customer_advance_data' in validate_data:
            for item in validate_data.get('cash_in_customer_advance_data', []):
                item['has_ar_invoice'] = False
                cls.common_valid_cash_in_customer_advance_data(item)
                validate_data['total_value'] = float(validate_data.get('total_value', 0)) + item['sum_payment_value']
        print('2. validate_cash_in_customer_advance_data --- ok')
        return validate_data

    @classmethod
    def validate_cash_in_ar_invoice_data(cls, validate_data):
        if 'cash_in_ar_invoice_data' in validate_data:
            for item in validate_data.get('cash_in_ar_invoice_data', []):
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
                cls.common_valid_cash_in_ar_invoice_data(item)
                validate_data['total_value'] = float(validate_data.get('total_value', 0)) + item['sum_payment_value']
        print('3. validate_cash_in_ar_invoice_data --- ok')
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

            if validate_data['bank_value'] > 0:
                if 'company_bank_account_id' in payment_method_data:
                    try:
                        company_bank_account = BankAccount.objects.get(
                            id=payment_method_data.get('company_bank_account_id')
                        )
                        validate_data['company_bank_account_id'] = str(company_bank_account.id)
                        validate_data['company_bank_account_data'] = {
                            'id': str(company_bank_account.id),
                            'bank_mapped_data': company_bank_account.bank_mapped_data,
                            'bank_account_owner': company_bank_account.bank_account_owner,
                            'bank_account_number': company_bank_account.bank_account_number,
                            'brand_name': company_bank_account.brand_name,
                            'brand_address': company_bank_account.brand_address
                        }
                    except BankAccount.DoesNotExist:
                        raise serializers.ValidationError({'company_bank_account_id': CashInflowMsg.BANK_NOT_EXIST})
                else:
                    raise serializers.ValidationError({'company_bank_account_id': CashInflowMsg.BANK_NOT_NULL})
            print('4. validate_payment_method_data --- ok')
            return validate_data
        raise serializers.ValidationError({'payment_method': CashInflowMsg.MISSING_PAYMENT_METHOD_INFO})

    @staticmethod
    def create_cif_item(cash_inflow_obj, cash_in_customer_advance_data, cash_in_ar_invoice_data):
        bulk_info = []
        bulk_info_detail = []
        for item in cash_in_customer_advance_data + cash_in_ar_invoice_data:
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
class CustomerAdvanceForCashInflowSerializer(serializers.ModelSerializer):
    sale_order = serializers.SerializerMethodField()
    value_balance = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrderPaymentStage
        fields = (
            'id',
            'sale_order',
            'remark',
            'term_data',
            'date',
            'date_type',
            'ratio',
            'value_before_tax',
            'invoice',
            'invoice_data',
            'value_total',
            'due_date',
            'order',
            'value_balance'
        )

    @classmethod
    def get_sale_order(cls, obj):
        sale_order_obj = obj.sale_order
        return {
            'id': sale_order_obj.id,
            'code': sale_order_obj.code,
            'title': sale_order_obj.title,
            'customer': {
                'id': sale_order_obj.customer_id,
                'code': sale_order_obj.customer.code,
                'name': sale_order_obj.customer.name,
                'tax_code': sale_order_obj.customer.tax_code
            } if sale_order_obj.customer else {}
        } if sale_order_obj else {}

    @classmethod
    def get_value_balance(cls, obj):
        cash_in_value = sum(
            CashInflowItem.objects.filter(
                cash_inflow__system_status=3, sale_order_stage=obj
            ).values_list('sum_payment_value', flat=True)
        )
        return obj.value_total - cash_in_value


class ARInvoiceListForCashInflowSerializer(serializers.ModelSerializer):
    customer_mapped = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    recon_balance = serializers.SerializerMethodField()
    payment_term_data = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'document_date',
            'posting_date',
            'customer_mapped',
            'document_type',
            'recon_total',
            'recon_balance',
            'payment_term_data'
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
    def get_recon_total(cls, obj):
        return obj.sum_after_tax_value

    @classmethod
    def get_recon_balance(cls, obj):
        # đã cấn trừ
        cash_in_value = sum(
            CashInflowItem.objects.filter(
                cash_inflow__system_status=3,
                ar_invoice=obj
            ).values_list('sum_payment_value', flat=True)
        )
        recon_balance = obj.sum_after_tax_value - cash_in_value
        return recon_balance

    @classmethod
    def get_payment_term_data(cls, obj):
        if obj.sale_order_mapped:
            return [{
                'id': item.id,
                'so_id': obj.sale_order_mapped_id,
                'so_code': obj.sale_order_mapped.code,
                'remark': item.remark,
                'term_data': item.term_data,
                'date': item.date,
                'date_type': item.date_type,
                'ratio': item.ratio,
                'value_before_tax': item.value_before_tax,
                'invoice': item.invoice,
                'invoice_data': item.invoice_data,
                'recon_total': item.value_total,
                'recon_balance': item.value_total - sum(
                    CashInflowItem.objects.filter(
                        cash_inflow__system_status=3,
                        ar_invoice=obj
                    ).values_list('sum_payment_value', flat=True)
                ),
                'due_date': item.due_date,
                'is_ar_invoice': item.is_ar_invoice,
                'order': item.order
            } for item in obj.sale_order_mapped.sale_order_payment_stage_sale_order.all()]
        return []
