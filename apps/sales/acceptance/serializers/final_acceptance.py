from rest_framework import serializers

from apps.sales.acceptance.models import FinalAcceptance, FinalAcceptanceIndicator


class FAIndicatorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinalAcceptanceIndicator
        fields = (
            'id',
        )


class FAIndicatorListSerializer(serializers.ModelSerializer):
    sale_order_indicator = serializers.SerializerMethodField()
    indicator = serializers.SerializerMethodField()
    sale_order = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    expense_item = serializers.SerializerMethodField()
    labor_item = serializers.SerializerMethodField()
    delivery_sub = serializers.SerializerMethodField()

    class Meta:
        model = FinalAcceptanceIndicator
        fields = (
            'id',
            'sale_order_indicator',
            'indicator',
            'sale_order',
            'payment',
            'expense_item',
            'labor_item',
            'delivery_sub',
            'indicator_value',
            'actual_value',
            'actual_value_after_tax',
            'different_value',
            'rate_value',
            'remark',
            'order',
            'is_indicator',
            'is_plan',
            'is_delivery',
            'is_payment',
        )

    @classmethod
    def get_sale_order_indicator(cls, obj):
        return {
            'id': obj.sale_order_indicator_id,
            'indicator_value': obj.sale_order_indicator.indicator_value,
            'indicator_rate': obj.sale_order_indicator.indicator_rate,
            'quotation_indicator_value': obj.sale_order_indicator.quotation_indicator_value,
            'quotation_indicator_rate': obj.sale_order_indicator.quotation_indicator_rate,
        } if obj.sale_order_indicator else {}

    @classmethod
    def get_indicator(cls, obj):
        return {
            'id': obj.indicator_id,
            'title': obj.indicator.title,
            'code': obj.indicator.code,
            'formula_data_show': obj.indicator.formula_data_show,
            'acceptance_affect_by': obj.indicator.acceptance_affect_by,
            'is_acceptance_editable': obj.indicator.is_acceptance_editable,
        } if obj.indicator else {}

    @classmethod
    def get_sale_order(cls, obj):
        return {
            'id': obj.sale_order_id,
            'title': obj.sale_order.title,
            'code': obj.sale_order.code,
        } if obj.sale_order else {}

    @classmethod
    def get_payment(cls, obj):
        return {
            'id': obj.payment_id,
            'title': obj.payment.title,
            'code': obj.payment.code,
        } if obj.payment else {}

    @classmethod
    def get_expense_item(cls, obj):
        return {
            'id': obj.expense_item_id,
            'title': obj.expense_item.title,
            'code': obj.expense_item.code,
        } if obj.expense_item else {}

    @classmethod
    def get_labor_item(cls, obj):
        return {
            'id': obj.labor_item_id,
            'title': obj.labor_item.title,
            'code': obj.labor_item.code,
        } if obj.labor_item else {}

    @classmethod
    def get_delivery_sub(cls, obj):
        return {
            'id': obj.delivery_sub_id,
            'title': obj.delivery_sub.title,
            'code': obj.delivery_sub.code,
        } if obj.delivery_sub else {}


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


class FinalAcceptanceUpdateSerializer(serializers.ModelSerializer):
    final_acceptance_indicator = serializers.JSONField(required=False)

    class Meta:
        model = FinalAcceptance
        fields = (
            'final_acceptance_indicator',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.get('final_acceptance_indicator', {}).items():
            fa_indicator = FinalAcceptanceIndicator.objects.filter(id=key).first()
            if fa_indicator:
                fa_indicator.actual_value = value.get('actual_value', 0)
                fa_indicator.different_value = value.get('different_value', 0)
                fa_indicator.rate_value = value.get('rate_value', 0)
                fa_indicator.save(update_fields=['actual_value', 'different_value', 'rate_value'])
        return instance
