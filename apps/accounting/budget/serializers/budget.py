from rest_framework import serializers

from apps.accounting.budget.models import BudgetLine


# PAYMENT PLAN BEGIN
class BudgetLineListSerializer(serializers.ModelSerializer):
    dimension_values_id = serializers.SerializerMethodField()
    value_available = serializers.SerializerMethodField()

    class Meta:
        model = BudgetLine
        fields = (
            'id',
            'remark',
            'unit_price',
            'quantity_planned',
            'quantity_consumed',
            'value_planned',
            'value_consumed',
            'value_available',
            'dimension_values_id',
            'order',
        )

    @classmethod
    def get_dimension_values_id(cls, obj):
        return list(obj.dimension_values.values_list('id', flat=True))

    @classmethod
    def get_value_available(cls, obj):
        return obj.value_planned - obj.value_consumed
