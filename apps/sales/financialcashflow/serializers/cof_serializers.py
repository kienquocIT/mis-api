from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, BankAccount
from apps.sales.apinvoice.models import APInvoice
from apps.sales.financialcashflow.models import CashInflow, CashInflowItem, CashInflowItemDetail
from apps.sales.purchasing.models import PurchaseOrderPaymentStage
from apps.shared import (
    AbstractListSerializerModel,
    AbstractCreateSerializerModel,
    AbstractDetailSerializerModel,
    CashInflowMsg
)


__all__ = [
    'AdvanceForSupplierForCashOutflowSerializer',
    'APInvoiceListForCashOutflowSerializer',
]


# main serializers



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
        return 0


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
        return 0

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
                'recon_balance': 0,
                'due_date': item.due_date,
                'is_ar_invoice': item.is_ap_invoice,
                'order': item.order
            } for item in obj.purchase_order_mapped.purchase_order_payment_stage_po.all()]
        return []
