from rest_framework import serializers
from apps.accounting.accountchart.models import AccountingAccount


class AccountingAccountListSerializer(serializers.ModelSerializer):
    currency_mapped = serializers.SerializerMethodField()

    class Meta:
        model = AccountingAccount
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


class AccountingAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingAccount
        fields = "__all__"


class AccountingAccountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingAccount
        fields = "__all__"
