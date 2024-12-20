from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.saleorder.models import SaleOrder

__all__ = [
    'ARInvoiceListForCashInflowSerializer',
]


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
            'name': obj.customer_mapped.name
        } if obj.customer_mapped else {}

    @classmethod
    def get_document_type(cls, obj):
        return _('AR Invoice')

    @classmethod
    def get_total(cls, obj):
        return sum([item.product_subtotal_final for item in obj.ar_invoice_items.all()])

    @classmethod
    def get_payment_value(cls, obj):
        return 0

    @classmethod
    def get_sale_order_data(cls, obj):
        return {
            'id': obj.sale_order_mapped_id,
            'code': obj.sale_order_mapped.code,
            'title': obj.sale_order_mapped.title,
            'payment_term': [{
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
                'due_date': item.due_date,
                'is_ar_invoice': item.is_ar_invoice,
                'order': item.order
            } for item in obj.sale_order_mapped.payment_stage_sale_order.all()],
        } if obj.sale_order_mapped else {}
