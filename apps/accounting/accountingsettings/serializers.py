from rest_framework import serializers
from apps.accounting.accountingsettings.models import (
    ChartOfAccounts, DefaultAccountDetermination,
    DEFAULT_ACCOUNT_DETERMINATION_TYPE
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


class DefaultAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_mapped = serializers.SerializerMethodField()
    default_account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = DefaultAccountDetermination
        fields = (
            'id',
            'title',
            'account_mapped',
            'default_account_determination_type',
            'default_account_determination_type_convert',
            'is_default'
        )

    @classmethod
    def get_account_mapped(cls, obj):
        return {
            'id': obj.account_mapped_id,
            'acc_code': obj.account_mapped.acc_code,
            'acc_name': obj.account_mapped.acc_name,
            'foreign_acc_name': obj.account_mapped.foreign_acc_name,
        } if obj.account_mapped else {}


    @classmethod
    def get_default_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.default_account_determination_type][1]


class DefaultAccountDeterminationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAccountDetermination
        fields = "__all__"


class DefaultAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAccountDetermination
        fields = "__all__"
