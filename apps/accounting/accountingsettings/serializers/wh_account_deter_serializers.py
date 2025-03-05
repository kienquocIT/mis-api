from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import (
    DEFAULT_ACCOUNT_DETERMINATION_TYPE, ChartOfAccounts
)
from apps.accounting.accountingsettings.models.wh_account_deter import WarehouseAccountDetermination


class WarehouseAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseAccountDetermination
        fields = (
            'id',
            'title',
            'warehouse_mapped_id',
            'account_mapped_data',
            'account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class WarehouseAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseAccountDetermination
        fields = "__all__"


class WarehouseAccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    replace_account = serializers.UUIDField()

    class Meta:
        model = WarehouseAccountDetermination
        fields = (
            'replace_account',
        )

    @classmethod
    def validate_replace_account(cls, value):
        try:
            return ChartOfAccounts.objects.get(id=value)
        except ChartOfAccounts.DoesNotExist:
            raise serializers.ValidationError({'replace_account': _('Replace account not found')})

    def update(self, instance, validated_data):
        replace_account = validated_data.pop('replace_account')
        instance.account_mapped = replace_account
        instance.account_mapped_data = {
            'id': str(replace_account.id),
            'acc_code': replace_account.acc_code,
            'acc_name': replace_account.acc_name,
            'foreign_acc_name': replace_account.foreign_acc_name,
        }
        instance.is_changed = True
        instance.save(update_fields=['account_mapped', 'account_mapped_data', 'is_changed'])
        return instance
