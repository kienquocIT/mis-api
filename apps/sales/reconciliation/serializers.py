from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models import Account
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.models import CashInflow
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem
from apps.shared import ReconMsg


__all__ = [
    'ReconListSerializer',
    'ReconCreateSerializer',
    'ReconDetailSerializer',
    'ARInvoiceListForReconSerializer',
    'CashInflowListForReconSerializer',
]

# main serializers
class ReconListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = Reconciliation
        fields = (
            'id',
            'code',
            'title',
            'business_partner_data',
            'date_created',
            'employee_created',
            'system_status',
            'system_auto_create',
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ReconCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    business_partner = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()
    recon_type = serializers.CharField()
    recon_item_data = serializers.JSONField(default=list)

    class Meta:
        model = Reconciliation
        fields = (
            'title',
            'business_partner',
            'posting_date',
            'document_date',
            'recon_type',
            'recon_item_data'
        )

    def validate(self, validate_data):
        ReconCommonFunction.validate_business_partner(validate_data)
        ReconCommonFunction.validate_recon_item_data(validate_data)
        return validate_data

    def create(self, validated_data):
        recon_item_data = validated_data.pop('recon_item_data')
        recon_obj = Reconciliation.objects.create(**validated_data, system_status=1)

        bulk_info = []
        for item in recon_item_data:
            bulk_info.append(ReconciliationItem(
                recon=recon_obj,
                recon_data={
                    'id': str(recon_obj.id),
                    'code': recon_obj.code,
                    'title': recon_obj.title
                },
                order=len(bulk_info),
                ar_invoice_id=item.get('ar_invoice_id'),
                ar_invoice_data=item.get('ar_invoice_data', {}),
                cash_inflow_id=item.get('cash_inflow_id'),
                cash_inflow_data=item.get('cash_inflow_data', {}),
                recon_balance=item.get('recon_balance', 0),
                recon_amount=item.get('recon_amount', 0),
                note=item.get('note', ''),
                accounting_account='1311'
            ))
        ReconciliationItem.objects.bulk_create(bulk_info)
        return recon_obj


class ReconDetailSerializer(serializers.ModelSerializer):
    recon_items_data = serializers.SerializerMethodField()

    class Meta:
        model = Reconciliation
        fields = (
            'id',
            'code',
            'title',
            'recon_type',
            'posting_date',
            'document_date',
            'business_partner_data',
            'recon_items_data',
            'system_status',
            'system_auto_create',
        )

    @classmethod
    def get_recon_items_data(cls, obj):
        return [{
            'id': item.id,
            'recon_data': item.recon_data,
            'order': item.order,
            'debit_doc_data': item.debit_doc_data,
            'credit_doc_data': item.credit_doc_data,
            'recon_total': item.recon_total,
            'recon_balance': item.recon_balance,
            'recon_amount': item.recon_amount,
            'note': item.note,
            'debit_account_data': item.debit_account_data,
            'credit_account_data': item.credit_account_data
        } for item in obj.recon_items.all()]


class ReconCommonFunction:
    @classmethod
    def validate_business_partner(cls, validate_data):
        if 'business_partner' in validate_data:
            try:
                business_partner_obj = Account.objects.get(id=validate_data.get('business_partner'))
                if not business_partner_obj.is_customer_account:
                    raise serializers.ValidationError({'business_partner': ReconMsg.ACCOUNT_NOT_CUSTOMER})
                validate_data['business_partner_data'] = {
                    'id': str(business_partner_obj.id),
                    'code': business_partner_obj.code,
                    'name': business_partner_obj.name,
                    'tax_code': business_partner_obj.tax_code,
                }
                print('1. validate_business_partner --- ok')
                return validate_data
            except Account.DoesNotExist:
                raise serializers.ValidationError({'business_partner': ReconMsg.CUSTOMER_NOT_EXIST})
        return None

    @classmethod
    def validate_recon_item_data(cls, validate_data):
        recon_item_data = validate_data.get('recon_item_data')
        for item in recon_item_data:
            if item.get('ar_invoice_id'):
                ar_invoice_obj = ARInvoice.objects.filter(id=item.get('ar_invoice_id')).first()
                if ar_invoice_obj:
                    item['ar_invoice_data'] = {
                        'id': str(ar_invoice_obj.id),
                        'code': ar_invoice_obj.code,
                        'title': ar_invoice_obj.title,
                        'type_doc': 'AR invoice',
                        'document_date': str(ar_invoice_obj.document_date),
                        'posting_date': str(ar_invoice_obj.posting_date),
                        'sum_total_value': sum(
                            item.product_subtotal_final for item in ar_invoice_obj.ar_invoice_items.all()
                        )
                    }
            if item.get('cash_inflow_id'):
                cif_obj = CashInflow.objects.filter(id=item.get('cash_inflow_id')).first()
                if cif_obj:
                    item['cash_inflow_data'] = {
                        'id': str(cif_obj.id),
                        'code': cif_obj.code,
                        'title': cif_obj.title,
                        'type_doc': 'Cash inflow',
                        'document_date': str(cif_obj.document_date),
                        'posting_date': str(cif_obj.posting_date),
                        'sum_total_value': cif_obj.total_value
                    }
        return recon_item_data

# related features
class ARInvoiceListForReconSerializer(serializers.ModelSerializer):
    document_type = serializers.SerializerMethodField()
    sum_total_value = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    cash_inflow_data = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'id',
            'title',
            'code',
            'document_date',
            'posting_date',
            'document_type',
            'sum_total_value',
            'recon_total',
            'cash_inflow_data'
        )

    @classmethod
    def get_document_type(cls, obj):
        return _('AR Invoice') if obj else ''

    @classmethod
    def get_sum_total_value(cls, obj):
        sum_total_value = sum(item.product_subtotal_final for item in obj.ar_invoice_items.all())
        return sum_total_value

    @classmethod
    def get_recon_total(cls, obj):
        print(obj)
        return 0

    @classmethod
    def get_cash_inflow_data(cls, obj):
        print(obj)
        cash_inflow_data = []
        return cash_inflow_data


class CashInflowListForReconSerializer(serializers.ModelSerializer):
    document_type = serializers.SerializerMethodField()
    sum_total_value = serializers.SerializerMethodField()
    recon_balance = serializers.SerializerMethodField()

    class Meta:
        model = CashInflow
        fields = (
            'id',
            'title',
            'code',
            'document_date',
            'posting_date',
            'document_type',
            'sum_total_value',
            'recon_balance',
        )

    @classmethod
    def get_document_type(cls, obj):
        return _('Cash inflow') if obj else ''

    @classmethod
    def get_sum_total_value(cls, obj):
        return obj.total_value

    @classmethod
    def get_recon_balance(cls, obj):
        print(obj)
        return 0
