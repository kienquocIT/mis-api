from rest_framework import serializers

from apps.accounting.budget.models import BudgetLine


# PAYMENT PLAN BEGIN
class BudgetLineListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BudgetLine
        fields = (
            'id',
            'remark',
            'price_planned',
            'quantity_planned',
            'quantity_consumed',
            'value_planned',
            'value_consumed',
            'order',
        )
