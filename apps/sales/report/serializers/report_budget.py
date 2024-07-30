from rest_framework import serializers

from apps.sales.budgetplan.models import BudgetPlanCompanyExpense, BudgetPlanGroupExpense
from apps.sales.cashoutflow.models import Payment


class BudgetReportCompanyListSerializer(serializers.ModelSerializer):
    expense_item = serializers.SerializerMethodField()

    class Meta:
        model = BudgetPlanCompanyExpense
        fields = (
            'order',
            'budget_plan',
            'expense_item',
            'company_month_list',
            'company_quarter_list',
            'company_year'
        )

    @classmethod
    def get_expense_item(cls, obj):
        return {
            'id': str(obj.expense_item_id),
            'code': obj.expense_item.code,
            'title': obj.expense_item.title
        } if obj.expense_item else {}


class BudgetReportGroupListSerializer(serializers.ModelSerializer):
    expense_item = serializers.SerializerMethodField()

    class Meta:
        model = BudgetPlanGroupExpense
        fields = (
            'order',
            'budget_plan',
            'expense_item',
            'group_month_list',
            'group_quarter_list',
            'group_year'
        )

    @classmethod
    def get_expense_item(cls, obj):
        return {
            'id': str(obj.expense_item_id),
            'code': obj.expense_item.code,
            'title': obj.expense_item.title
        } if obj.expense_item else {}


class PaymentListSerializerForBudgetPlan(serializers.ModelSerializer):
    expense_items = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            'id',
            'code',
            'title',
            'expense_items'
        )

    @classmethod
    def get_expense_items(cls, obj):
        all_expense_items_mapped = []
        for item in obj.payment.all():
            all_expense_items_mapped.append(
                {
                    'id': item.expense_type_id,
                    'code': item.expense_type.code,
                    'title': item.expense_type.title,
                    'value': item.expense_after_tax_price
                } if item.expense_type else {}
            )
        return all_expense_items_mapped
