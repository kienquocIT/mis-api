from rest_framework import serializers

from apps.sales.acceptance.models import FinalAcceptance, FinalAcceptanceIndicator


class FAIndicatorListSerializer(serializers.ModelSerializer):
    sale_order_indicator = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()

    class Meta:
        model = FinalAcceptanceIndicator
        fields = (
            'id',
            'sale_order_indicator',
            'sale_order',
            'indicator_value',
            'actual_value',
            'different_value',
            'rate_value',
            'remark',
            'order',
            'is_indicator',
            'is_sale_order',
            'is_delivery',
            'is_payment',
        )

    @classmethod
    def get_sale_order_indicator(cls, obj):
        return {
            'id': obj.sale_order_indicator_id,
            'indicator': {
                'id': obj.sale_order_indicator.quotation_indicator_id,
                'title': obj.sale_order_indicator.quotation_indicator.title,
                'code': obj.sale_order_indicator.quotation_indicator.code,
            } if obj.sale_order_indicator.quotation_indicator else {},
            'indicator_value': obj.sale_order_indicator.indicator_value,
            'indicator_rate': obj.sale_order_indicator.indicator_rate,
            'quotation_indicator_value': obj.sale_order_indicator.quotation_indicator_value,
            'quotation_indicator_rate': obj.sale_order_indicator.quotation_indicator_rate,
        } if obj.sale_order_indicator else {}

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'title': obj.sale_order.title,
            'code': obj.sale_order.code,
        } if obj.sale_order else {}


class FinalAcceptanceListSerializer(serializers.ModelSerializer):
    final_acceptance_indicator = serializers.SerializerMethodField()

    class Meta:
        model = FinalAcceptance
        fields = (
            'id',
            'final_acceptance_indicator',
        )

    @classmethod
    def get_final_acceptance_indicator(cls, obj):
        return FAIndicatorListSerializer(obj.fa_indicator_final_acceptance.all(), many=True).data
