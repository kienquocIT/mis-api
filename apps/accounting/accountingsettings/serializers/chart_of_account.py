from rest_framework import serializers
from apps.accounting.accountingsettings.models.chart_of_account import (
    ChartOfAccounts, ChartOfAccountsSummarize
)


class ChartOfAccountsListSerializer(serializers.ModelSerializer):

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
            'currency_mapped_data'
        )


class ChartOfAccountsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = "__all__"

    def create(self, validated_data):
        instance = ChartOfAccounts.objects.create(**validated_data)
        return instance


class ChartOfAccountsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartOfAccounts
        fields = "__all__"
