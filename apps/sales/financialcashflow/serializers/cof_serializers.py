from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, BankAccount
from apps.sales.apinvoice.models import APInvoice
from apps.sales.financialcashflow.models import CashOutflow, CashOutflowItem, CashOutflowItemDetail
from apps.sales.purchasing.models import PurchaseOrderPaymentStage
from apps.sales.reconciliation.models import ReconciliationItem
from apps.shared import (
    AbstractListSerializerModel,
    AbstractCreateSerializerModel,
    AbstractDetailSerializerModel,
    CashOutflowMsg
)


__all__ = [
    'CashOutflowListSerializer',
    'CashOutflowCreateSerializer',
    'CashOutflowDetailSerializer',
    'CashOutflowUpdateSerializer',
    'AdvanceForSupplierForCashOutflowSerializer',
    'APInvoiceListForCashOutflowSerializer',
]

# main serializers
class CashOutflowListSerializer(AbstractListSerializerModel):
    class Meta:
        model = CashOutflow
        fields = (
            'id',
            'code',
            'title',
            'cof_type',
            'supplier_data',
            'total_value',
            'date_created',
            'system_status'
        )


class CashOutflowCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    cof_type = serializers.IntegerField()
    supplier_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cash_out_advance_for_supplier_data = serializers.JSONField(default=list)
    # cash_out_advance_for_supplier_data = [{
    #     'purchase_order_id': uuid,
    #     'sum_balance_value': number,
    #     'sum_payment_value': number,
    #     'detail_payment': [{
    #         'po_pm_stage_id': uuid,
    #         'balance_value': number,
    #         'payment_value': number,
    #     }]
    # }]
    cash_out_ap_invoice_data = serializers.JSONField(default=list)
    # cash_out_ap_invoice_data = [{
    #     'ap_invoice_id': uuid,
    #     'purchase_order_id': uuid,
    #     'sum_balance_value': number,
    #     'sum_payment_value': number,
    #     'discount_payment': number,
    #     'discount_value': number,
    #     'detail_payment': [{
    #         'po_pm_stage_id': uuid,
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
        model = CashOutflow
        fields = (
            'title',
            'cof_type',
            'supplier_id',
            'posting_date',
            'document_date',
            'description',
            'advance_for_supplier_value',
            'payment_to_customer_value',
            'advance_for_employee_value',
            # detail data
            'cash_out_advance_for_supplier_data',
            'cash_out_ap_invoice_data',
            # payment method data
            'payment_method_data',
        )

    def validate(self, validate_data):
        CashOutflowCommonFunction.validate_cof_type(validate_data)
        CashOutflowCommonFunction.validate_supplier_id(validate_data)
        if validate_data.get('cof_type') == 0:
            validate_data['total_value'] = float(validate_data.get('advance_for_supplier_value', 0))
        if validate_data.get('cof_type') == 1:
            validate_data['total_value'] = float(validate_data.get('payment_to_customer_value', 0))
        if validate_data.get('cof_type') == 2:
            validate_data['total_value'] = float(validate_data.get('advance_for_employee_value', 0))
        CashOutflowCommonFunction.validate_cash_out_advance_for_supplier_data(validate_data)
        CashOutflowCommonFunction.validate_cash_out_ap_invoice_data(validate_data)
        CashOutflowCommonFunction.validate_payment_method_data(validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        cash_out_advance_for_supplier_data = validated_data.pop('cash_out_advance_for_supplier_data', [])
        cash_out_ap_invoice_data = validated_data.pop('cash_out_ap_invoice_data', [])

        cash_outflow_obj = CashOutflow.objects.create(**validated_data)

        CashOutflowCommonFunction.create_cof_item(
            cash_outflow_obj, cash_out_advance_for_supplier_data, cash_out_ap_invoice_data
        )

        return cash_outflow_obj


class CashOutflowDetailSerializer(AbstractDetailSerializerModel):
    cash_out_advance_for_supplier_data = serializers.SerializerMethodField()
    cash_out_ap_invoice_data = serializers.SerializerMethodField()

    class Meta:
        model = CashOutflow
        fields = (
            'id',
            'code',
            'title',
            'cof_type',
            'posting_date',
            'document_date',
            'description',
            'supplier_data',
            'advance_for_supplier_value',
            'payment_to_customer_value',
            'advance_for_employee_value',
            'cash_out_advance_for_supplier_data',
            'cash_out_ap_invoice_data',
            'total_value',
            'cash_value',
            'bank_value',
            'company_bank_account_data'
        )

    @classmethod
    def get_cash_out_advance_for_supplier_data(cls, obj):
        cash_out_advance_for_supplier_data = []
        for item in obj.cash_outflow_item_cash_outflow.filter(has_ap_invoice=False):
            cash_out_advance_for_supplier_data.append({
                'id': item.id,
                'cash_outflow_data': item.cash_outflow_data,
                'purchase_order_stage_data': item.purchase_order_stage_data,
                'purchase_order_data': item.purchase_order_data,
                'sum_balance_value': item.sum_balance_value,
                'sum_payment_value': item.sum_payment_value,
            })
        return cash_out_advance_for_supplier_data

    @classmethod
    def get_cash_out_ap_invoice_data(cls, obj):
        cash_out_ap_invoice_data = []
        for item in obj.cash_outflow_item_cash_outflow.filter(has_ap_invoice=True):
            cash_out_ap_invoice_data.append({
                'id': item.id,
                'cash_outflow_data': item.cash_outflow_data,
                'has_ap_invoice': item.has_ap_invoice,
                'ap_invoice_data': item.ap_invoice_data,
                'purchase_order_data': item.purchase_order_data,
                'sum_balance_value': item.sum_balance_value,
                'sum_payment_value': item.sum_payment_value,
                'detail_payment': [{
                    'id': detail.id,
                    'po_pm_stage_data': detail.po_pm_stage_data,
                    'balance_value': detail.balance_value,
                    'payment_value': detail.payment_value
                } for detail in item.cash_outflow_item_detail_cash_outflow_item.all()],
            })
        return cash_out_ap_invoice_data


class CashOutflowUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    supplier_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cash_out_advance_for_supplier_data = serializers.JSONField(default=list)
    cash_out_ap_invoice_data = serializers.JSONField(default=list)
    payment_method_data = serializers.JSONField(default=dict)

    class Meta:
        model = CashOutflow
        fields = (
            'title',
            'cof_type',
            'supplier_id',
            'posting_date',
            'document_date',
            'description',
            'advance_for_employee_value',
            'payment_to_customer_value',
            'advance_for_supplier_value',
            # detail data
            'cash_out_advance_for_supplier_data',
            'cash_out_ap_invoice_data',
            # payment method data
            'payment_method_data',
        )

    def validate(self, validate_data):
        return CashOutflowCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        cash_out_advance_for_supplier_data = validated_data.pop('cash_out_advance_for_supplier_data', [])
        cash_out_ap_invoice_data = validated_data.pop('cash_out_ap_invoice_data', [])

        if len(cash_out_advance_for_supplier_data) > 0:
            validated_data['no_ap_invoice_value'] = validated_data.get('total_value', 0)
        elif len(cash_out_ap_invoice_data) > 0:
            validated_data['has_ap_invoice_value'] = validated_data.get('total_value', 0)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        CashOutflowCommonFunction.create_cof_item(
            instance, cash_out_advance_for_supplier_data, cash_out_ap_invoice_data
        )
        return instance


class CashOutflowCommonFunction:
    @classmethod
    def validate_cof_type(cls, validate_data):
        if 'cof_type' not in validate_data:
            raise serializers.ValidationError({'cof_type': CashOutflowMsg.COF_TYPE_NOT_NULL})
        if validate_data.get('cof_type') not in [0, 1, 2, 3]:
            raise serializers.ValidationError({'cof_type': CashOutflowMsg.COF_TYPE_NOT_VALID})
        print('1. validate_cof_type --- ok')
        return validate_data

    @classmethod
    def validate_supplier_id(cls, validate_data):
        if 'supplier_id' in validate_data:
            if validate_data.get('supplier_id'):
                try:
                    supplier = Account.objects.get(id=validate_data.get('supplier_id'))
                    if not supplier.is_supplier_account:
                        raise serializers.ValidationError({'supplier_id': CashOutflowMsg.ACCOUNT_NOT_SUPPLIER})
                    validate_data['supplier_id'] = str(supplier.id)
                    validate_data['supplier_data'] = {
                        'id': str(supplier.id),
                        'code': supplier.code,
                        'name': supplier.name,
                        'tax_code': supplier.tax_code,
                    }
                    print('2. validate_supplier_id --- ok')
                    return validate_data
                except Account.DoesNotExist:
                    raise serializers.ValidationError({'supplier_id': CashOutflowMsg.SUPPLIER_NOT_EXIST})
        raise serializers.ValidationError({'supplier_id': CashOutflowMsg.SUPPLIER_NOT_NULL})

    @staticmethod
    def common_valid_cash_out_ap_invoice_data(item):
        # check po
        ap_invoice_obj = APInvoice.objects.filter(id=item.get('ap_invoice_id')).first()
        if not ap_invoice_obj:
            raise serializers.ValidationError({'ap_invoice_id': CashOutflowMsg.AP_INVOICE_NOT_EXIST})
        if ap_invoice_obj.purchase_order_mapped:
            item['purchase_order_id'] = str(ap_invoice_obj.purchase_order_mapped_id)
            item['purchase_order_data'] = {
                'id': str(ap_invoice_obj.purchase_order_mapped_id),
                'code': ap_invoice_obj.purchase_order_mapped.code,
                'title': ap_invoice_obj.purchase_order_mapped.title
            }
        else:
            raise serializers.ValidationError({'purchase_order_id': CashOutflowMsg.PURCHASE_ORDER_NOT_EXIST})

        for row in item.get('detail_payment', []):
            purchase_order_stage = PurchaseOrderPaymentStage.objects.filter(id=row.get('po_pm_stage_id')).first()
            if not purchase_order_stage:
                raise serializers.ValidationError({'po_pm_stage_id': CashOutflowMsg.PURCHASE_ORDER_STAGE_NOT_EXIST})
            row['po_pm_stage_data'] = {
                'id': str(purchase_order_stage.id),
                'remark': purchase_order_stage.remark,
                'date': str(purchase_order_stage.date),
                'date_type': purchase_order_stage.date_type,
                'ratio': purchase_order_stage.ratio,
                'value_before_tax': purchase_order_stage.value_before_tax,
                'invoice': purchase_order_stage.invoice,
                'invoice_data': purchase_order_stage.invoice_data,
                'value_total': purchase_order_stage.value_total,
                'due_date': str(purchase_order_stage.due_date),
                'is_ap_invoice': purchase_order_stage.is_ap_invoice,
                'order': purchase_order_stage.order,
            }

        item['sum_balance_value'] = float(item.get('sum_balance_value', 0))
        item['sum_payment_value'] = float(item.get('sum_payment_value', 0))
        return True

    @staticmethod
    def common_valid_cash_out_advance_for_supplier_data(item):
        # check po
        purchase_order_stage = PurchaseOrderPaymentStage.objects.filter(id=item.get('purchase_order_stage_id')).first()
        if not purchase_order_stage:
            raise serializers.ValidationError(
                {'purchase_order_stage_id': CashOutflowMsg.PURCHASE_ORDER_STAGE_NOT_EXIST}
            )
        item['purchase_order_stage_id'] = str(purchase_order_stage.id)
        item['purchase_order_stage_data'] = {
            'id': str(purchase_order_stage.id),
            'remark': purchase_order_stage.remark,
            'date': str(purchase_order_stage.date),
            'date_type': purchase_order_stage.date_type,
            'ratio': purchase_order_stage.ratio,
            'value_before_tax': purchase_order_stage.value_before_tax,
            'invoice': purchase_order_stage.invoice,
            'invoice_data': purchase_order_stage.invoice_data,
            'value_total': purchase_order_stage.value_total,
            'due_date': str(purchase_order_stage.due_date),
            'is_ap_invoice': purchase_order_stage.is_ap_invoice,
            'order': purchase_order_stage.order,
        }
        if purchase_order_stage.purchase_order:
            item['purchase_order_id'] = str(purchase_order_stage.purchase_order_id)
            item['purchase_order_data'] = {
                'id': str(purchase_order_stage.purchase_order_id),
                'code': purchase_order_stage.purchase_order.code,
                'title': purchase_order_stage.purchase_order.title
            }
        else:
            raise serializers.ValidationError({'purchase_order_id': CashOutflowMsg.PURCHASE_ORDER_NOT_EXIST})

        item['sum_balance_value'] = float(item.get('sum_balance_value', 0))
        item['sum_payment_value'] = float(item.get('sum_payment_value', 0))
        return True

    @classmethod
    def validate_cash_out_advance_for_supplier_data(cls, validate_data):
        if 'cash_out_advance_for_supplier_data' in validate_data:
            no_ap_invoice_value = 0
            for item in validate_data.get('cash_out_advance_for_supplier_data', []):
                item['has_ap_invoice'] = False
                cls.common_valid_cash_out_advance_for_supplier_data(item)
                no_ap_invoice_value += item.get('sum_payment_value', 0)
                validate_data['total_value'] = float(
                    validate_data.get('total_value', 0)
                ) + item.get('sum_payment_value', 0)
            validate_data['no_ap_invoice_value'] = no_ap_invoice_value
        print('3. validate_cash_out_advance_for_supplier_data --- ok')
        return validate_data

    @classmethod
    def validate_cash_out_ap_invoice_data(cls, validate_data):
        if 'cash_out_ap_invoice_data' in validate_data:
            has_ap_invoice_value = 0
            for item in validate_data.get('cash_out_ap_invoice_data', []):
                item['has_ap_invoice'] = True
                # check ar invoice
                ap_invoice = APInvoice.objects.filter(id=item.get('ap_invoice_id')).first()
                if not ap_invoice:
                    raise serializers.ValidationError({'ap_invoice_id': CashOutflowMsg.AP_INVOICE_NOT_EXIST})
                item['ap_invoice_id'] = str(ap_invoice.id)
                item['ap_invoice_data'] = {
                    'id': str(ap_invoice.id),
                    'code': ap_invoice.code,
                    'title': ap_invoice.title,
                    'type_doc': 'AR invoice',
                    'document_date': str(ap_invoice.document_date),
                    'posting_date': str(ap_invoice.posting_date),
                    'sum_total_value': sum(item.product_subtotal_final for item in ap_invoice.ap_invoice_items.all())
                }
                cls.common_valid_cash_out_ap_invoice_data(item)
                has_ap_invoice_value += item.get('sum_payment_value', 0)
                validate_data['total_value'] = float(
                    validate_data.get('total_value', 0)
                ) + item.get('sum_payment_value', 0)
            validate_data['has_ap_invoice_value'] = has_ap_invoice_value
        print('4. validate_cash_out_ap_invoice_data --- ok')
        return validate_data

    @classmethod
    def validate_payment_method_data(cls, validate_data):
        payment_method_data = validate_data.pop('payment_method_data', {})
        if all(key in payment_method_data for key in ['cash_value', 'bank_value']):
            # check cof total_value == cash_value + bank_value ?
            validate_data['cash_value'] = float(payment_method_data.get('cash_value', 0))
            validate_data['bank_value'] = float(payment_method_data.get('bank_value', 0))
            validate_data['total_value'] = float(validate_data.get('total_value', 0))
            if validate_data['cash_value'] + validate_data['bank_value'] != validate_data['total_value']:
                raise serializers.ValidationError({'payment_method': CashOutflowMsg.COF_TOTAL_VALUE_NOT_MATCH})

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
                        raise serializers.ValidationError({'company_bank_account_id': CashOutflowMsg.BANK_NOT_EXIST})
                else:
                    raise serializers.ValidationError({'company_bank_account_id': CashOutflowMsg.BANK_NOT_NULL})
            print('5. validate_payment_method_data --- ok')
            return validate_data
        raise serializers.ValidationError({'payment_method': CashOutflowMsg.MISSING_PAYMENT_METHOD_INFO})

    @staticmethod
    def create_cof_item(cash_outflow_obj, cash_out_advance_for_supplier_data, cash_out_ap_invoice_data):
        bulk_info = []
        bulk_info_detail = []
        for item in cash_out_advance_for_supplier_data + cash_out_ap_invoice_data:
            detail_payment = item.pop('detail_payment', [])
            cof_item_obj = CashOutflowItem(
                cash_outflow=cash_outflow_obj,
                cash_outflow_data={
                    'id': str(cash_outflow_obj.id),
                    'code': cash_outflow_obj.code,
                    'title': cash_outflow_obj.title
                } if cash_outflow_obj else {},
                **item
            )
            bulk_info.append(cof_item_obj)
            for detail in detail_payment:
                bulk_info_detail.append(CashOutflowItemDetail(
                    cash_outflow_item=cof_item_obj,
                    **detail
                ))
        cash_outflow_obj.cash_outflow_item_cash_outflow.all().delete()
        CashOutflowItem.objects.bulk_create(bulk_info)
        CashOutflowItemDetail.objects.bulk_create(bulk_info_detail)
        print('* create_cof_item --- ok')
        return True

# related serializers
class AdvanceForSupplierForCashOutflowSerializer(serializers.ModelSerializer):
    purchase_order = serializers.SerializerMethodField()
    value_balance = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderPaymentStage
        fields = (
            'id',
            'purchase_order',
            'remark',
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
    def get_purchase_order(cls, obj):
        purchase_order_obj = obj.purchase_order
        return {
            'id': purchase_order_obj.id,
            'code': purchase_order_obj.code,
            'title': purchase_order_obj.title,
            'supplier': {
                'id': purchase_order_obj.supplier_id,
                'code': purchase_order_obj.supplier.code,
                'name': purchase_order_obj.supplier.name,
                'tax_code': purchase_order_obj.supplier.tax_code
            } if purchase_order_obj.supplier else {}
        } if purchase_order_obj else {}

    @classmethod
    def get_value_balance(cls, obj):
        cash_out_value = sum(
            CashOutflowItem.objects.filter(
                cash_outflow__system_status=3, purchase_order_stage=obj
            ).values_list('sum_payment_value', flat=True)
        )
        return obj.value_total - cash_out_value


class APInvoiceListForCashOutflowSerializer(serializers.ModelSerializer):
    supplier_mapped = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    recon_balance = serializers.SerializerMethodField()
    payment_term_data = serializers.SerializerMethodField()

    class Meta:
        model = APInvoice
        fields = (
            'id',
            'title',
            'code',
            'document_date',
            'posting_date',
            'supplier_mapped',
            'document_type',
            'recon_total',
            'recon_balance',
            'payment_term_data'
        )

    @classmethod
    def get_supplier_mapped(cls, obj):
        return {
            'id': obj.supplier_mapped_id,
            'code': obj.supplier_mapped.code,
            'name': obj.supplier_mapped.name,
            'tax_code': obj.supplier_mapped.tax_code
        } if obj.supplier_mapped else {}

    @classmethod
    def get_document_type(cls, obj):
        return _('AP Invoice') if obj else ''

    @classmethod
    def get_recon_total(cls, obj):
        return obj.sum_after_tax_value

    @classmethod
    def get_recon_balance(cls, obj):
        # đã cấn trừ
        sum_recon_amount = sum(item.recon_amount for item in ReconciliationItem.objects.filter(
            credit_doc_id=str(obj.id),
        ))
        recon_balance = obj.sum_after_tax_value - sum_recon_amount
        return recon_balance

    @classmethod
    def get_payment_term_data(cls, obj):
        if obj.purchase_order_mapped:
            return [{
                'id': item.id,
                'po_id': obj.purchase_order_mapped_id,
                'po_code': obj.purchase_order_mapped.code,
                'remark': item.remark,
                'date': item.date,
                'date_type': item.date_type,
                'ratio': item.ratio,
                'value_before_tax': item.value_before_tax,
                'invoice': item.invoice,
                'invoice_data': item.invoice_data,
                'recon_total': item.value_total,
                'recon_balance': item.value_total - sum(
                    CashOutflowItem.objects.filter(
                        cash_outflow__system_status=3,
                        ap_invoice=obj
                    ).values_list('sum_payment_value', flat=True)
                ),
                'due_date': item.due_date,
                'is_ap_invoice': item.is_ap_invoice,
                'order': item.order
            } for item in obj.purchase_order_mapped.purchase_order_payment_stage_po.all()]
        return []
