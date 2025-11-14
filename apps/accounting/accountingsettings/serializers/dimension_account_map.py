from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models import AccountDimensionMap, ChartOfAccounts, Dimension

__all__ = [
    'DimensionListForAccountingAccountSerializer',
    'AccountDimensionMapCreateSerializer',
    'AccountDimensionMapDetailSerializer',
    'AccountDimensionMapUpdateSerializer'
]

class DimensionListForAccountingAccountSerializer(serializers.ModelSerializer):
    dimension_map_data = serializers.SerializerMethodField()

    class Meta:
        model = ChartOfAccounts
        fields = (
            'id',
            'acc_code',
            'acc_name',
            'dimension_map_data'
        )

    @classmethod
    def get_dimension_map_data(cls, obj):
        current_dimension_list = Dimension.objects.filter_on_company()
        data = []
        for item in current_dimension_list:
            account_dimension_map = item.map_finance_accounts.filter(account=obj).first()
            data.append({
                'id': item.id,
                'code': item.code,
                'title': item.title,
                'account_dimension_map': {
                    'id': account_dimension_map.id,
                    'status': account_dimension_map.status,
                    'status_text': account_dimension_map.get_status_display(),
                } if account_dimension_map else None,
            })
        return data


class AccountDimensionMapCreateSerializer(serializers.ModelSerializer):
    account_id = serializers.UUIDField(error_messages={
        'required': _('Account is required.'),
    })
    dimension_id = serializers.UUIDField(error_messages={
        'required': _('Dimension is required.'),
    })

    class Meta:
        model = AccountDimensionMap
        fields = (
            'account_id',
            'dimension_id',
            'status'
        )

    @classmethod
    def validate_account_id(cls, value):
        try:
            return ChartOfAccounts.objects.get(id=value).id
        except ChartOfAccounts.DoesNotExist:
            raise serializers.ValidationError({"Account": _("Account does not exist.")})

    @classmethod
    def validate_dimension_id(cls, value):
        try:
            return Dimension.objects.get(id=value).id
        except Dimension.DoesNotExist:
            raise serializers.ValidationError({"Dimension": _("Dimension does not exist.")})


class AccountDimensionMapUpdateSerializer(serializers.ModelSerializer):
    account_id = serializers.UUIDField(error_messages={
        'required': _('Account is required.'),
    })
    dimension_id = serializers.UUIDField(error_messages={
        'required': _('Dimension is required.'),
    })

    class Meta:
        model = AccountDimensionMap
        fields = (
            'account_id',
            'dimension_id',
            'status'
        )

    @classmethod
    def validate_account_id(cls, value):
        try:
            return ChartOfAccounts.objects.get(id=value).id
        except ChartOfAccounts.DoesNotExist:
            raise serializers.ValidationError({"Account": _("Account does not exist.")})

    @classmethod
    def validate_dimension_id(cls, value):
        try:
            return Dimension.objects.get(id=value).id
        except Dimension.DoesNotExist:
            raise serializers.ValidationError({"Dimension": _("Dimension does not exist.")})


class AccountDimensionMapDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDimensionMap
        fields = (
            'account_id',
            'dimension_id',
            'status'
        )
