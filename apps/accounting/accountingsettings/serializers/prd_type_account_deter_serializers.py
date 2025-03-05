from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import (
    DEFAULT_ACCOUNT_DETERMINATION_TYPE,
    ChartOfAccounts
)
from apps.accounting.accountingsettings.models.prd_type_account_deter import ProductTypeAccountDetermination


class ProductTypeAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = ProductTypeAccountDetermination
        fields = (
            'id',
            'title',
            'product_type_mapped_id',
            'account_mapped_data',
            'account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class ProductTypeAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTypeAccountDetermination
        fields = "__all__"


class ProductTypeAccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    replace_account = serializers.UUIDField()

    class Meta:
        model = ProductTypeAccountDetermination
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
