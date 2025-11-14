from rest_framework import serializers

from apps.accounting.budget.models import BudgetLine


# PAYMENT PLAN BEGIN
class BudgetLineListSerializer(serializers.ModelSerializer):
    dimension_values_id = serializers.SerializerMethodField()

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
            'dimension_values_id',
            'order',
        )

    @classmethod
    def get_dimension_values_id(cls, obj):
        return list(obj.dimension_values.values_list('id', flat=True))
