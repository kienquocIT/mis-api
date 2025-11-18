from rest_framework import serializers

from apps.accounting.budget.models import BudgetLine, BudgetLineTransaction, Budget
from apps.shared import BaseMsg


class BudgetListSerializer(serializers.ModelSerializer):
    budget_line_data = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            'id',
            'budget_line_data',
            'system_status',
            'date_approved',
        )

    @classmethod
    def get_budget_line_data(cls, obj):
        return BudgetLineListSerializer(
            BudgetLine.objects.filter_on_company(budget=obj), many=True
        ).data


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


class BudgetLineTransactionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BudgetLineTransaction
        fields = (
            'budget_line_id',
            'budget_line_data',
            'dimension_first_data',
            'dimension_value_first_data',
            'dimension_second_data',
            'dimension_value_second_data',
            'value_consume',
            'order',
        )


class BudgetLineTransactionCreateSerializer(serializers.ModelSerializer):
    budget_line_id = serializers.UUIDField()

    class Meta:
        model = BudgetLineTransaction
        fields = (
            'budget_line_id',
            'budget_line_data',
            'dimension_first_data',
            'dimension_value_first_data',
            'dimension_second_data',
            'dimension_value_second_data',
            'value_consume',
            'order',
        )

    @classmethod
    def validate_budget_line_id(cls, value):
        try:
            return str(BudgetLine.objects.get_on_company(id=value).id)
        except BudgetLine.DoesNotExist:
            raise serializers.ValidationError({'budget line': BaseMsg.NOT_EXIST})
