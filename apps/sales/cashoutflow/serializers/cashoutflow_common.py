from rest_framework import serializers
from apps.sales.quotation.models import Quotation
from apps.sales.saleorder.models import SaleOrder
from apps.shared import AbstractListSerializerModel


class CashOutflowQuotationListSerializer(AbstractListSerializerModel):
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = (
            'id',
            'title',
            'code',
            'sale_order'
        )

    @classmethod
    def get_sale_order(cls, obj):
        sale_order_obj = obj.sale_order_quotation.filter(system_status=3).first()
        return {
            'id': sale_order_obj.id,
            'title': sale_order_obj.title,
            'code': sale_order_obj.code,
        } if sale_order_obj else {}


class CashOutflowSaleOrderListSerializer(AbstractListSerializerModel):
    quotation = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = (
            'id',
            'title',
            'code',
            'quotation'
        )

    @classmethod
    def get_quotation(cls, obj):
        return {
            'id': obj.quotation_id,
            'title': obj.quotation.title,
            'code': obj.quotation.code,
        } if obj.quotation else {}
