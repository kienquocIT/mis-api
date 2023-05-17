from rest_framework import serializers

from apps.masterdata.saledata.models import GoodReceipt

__all__ = ['GoodReceiptListSerializer']


class GoodReceiptListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()

    class Meta:
        model = GoodReceipt
        fields = (
            'id',
            'code',
            'title',
            'supplier',
            'posting_date',
            'system_status'
        )

    @classmethod
    def get_supplier(cls, obj):
        if obj:
            return {
                'id': obj.supplier_id,
                'title': obj.supplier.title,
                'code': obj.supplier.code
            }
        return {}
