from rest_framework import serializers
from apps.accounting.accountingsettings.models.chart_of_account import (
    ChartOfAccounts
)


class ChartOfAccountsListSerializer(serializers.ModelSerializer):
    currency_mapped = serializers.SerializerMethodField()

    class Meta:
        model = ChartOfAccounts
        fields = (
            'id',
            'order',
            'acc_code',
            'acc_name',
            'foreign_acc_name',
            'acc_status',
            'acc_type',
            'parent_account',
            'has_child',
            'level',
            'is_account',
            'control_account',
            'is_all_currency',
            'is_default',
            'currency_mapped'
        )

    @classmethod
    def get_currency_mapped(cls, obj):
        return {
            'id': obj.currency_mapped_id,
            'abbreviation': obj.currency_mapped.abbreviation,
            'title': obj.currency_mapped.title
        } if obj.currency_mapped else {}


class ChartOfAccountsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = "__all__"


class ChartOfAccountsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = "__all__"
