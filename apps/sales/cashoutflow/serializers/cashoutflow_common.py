from rest_framework import serializers

from apps.masterdata.saledata.models import Account
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


class CashOutflowSupplierListSerializer(serializers.ModelSerializer):
    bank_accounts_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            'bank_accounts_mapped',
        )

    @classmethod
    def get_bank_accounts_mapped(cls, obj):
        return [{
            'id': str(item.id),
            'bank_country_id': str(item.country_id),
            'bank_name': item.bank_name,
            'bank_code': item.bank_code,
            'bank_account_name': item.bank_account_name,
            'bank_account_number': item.bank_account_number,
            'bic_swift_code': item.bic_swift_code,
            'is_default': item.is_default
        } for item in obj.account_banks_mapped.all()]
