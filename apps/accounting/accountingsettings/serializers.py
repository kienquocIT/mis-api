from rest_framework import serializers
from apps.accounting.accountingsettings.models import ChartOfAccounts, DefaultAccountDefinition


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


class DefaultAccountDefinitionListSerializer(serializers.ModelSerializer):
    account_mapped = serializers.SerializerMethodField()

    class Meta:
        model = DefaultAccountDefinition
        fields = (
            'id',
            'title',
            'account_mapped',
            'type',
            'is_default'
        )

    @classmethod
    def get_account_mapped(cls, obj):
        return {
            'id': obj.account_mapped_id,
            'acc_code': obj.account_mapped.acc_code,
            'acc_name': obj.account_mapped.acc_name
        } if obj.account_mapped else {}


class DefaultAccountDefinitionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAccountDefinition
        fields = "__all__"


class DefaultAccountDefinitionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAccountDefinition
        fields = "__all__"
