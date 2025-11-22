from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models.chart_of_account import (
    ChartOfAccounts
)
from apps.accounting.accountingsettings.models.account_determination import (
    ACCOUNT_DETERMINATION_TYPE,
    AccountDetermination, AccountDeterminationSub,
)


class AccountDeterminationListSerializer(serializers.ModelSerializer):
    account_mapped = serializers.SerializerMethodField()
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = AccountDetermination
        fields = (
            'id',
            'title',
            'foreign_title',
            'account_mapped',
            'account_determination_type',
            'account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_mapped(cls, obj):
        return [item.account_mapped_data for item in obj.account_determination_sub.all()]

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class AccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetermination
        fields = "__all__"


class AccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    replace_account = serializers.JSONField(default=list)

    class Meta:
        model = AccountDetermination
        fields = (
            'replace_account',
        )

    @classmethod
    def validate_replace_account(cls, replace_account):
        if len([replace_account]) == 1:
            replace_account_list = []
            for account_id in [replace_account]:
                account_mapped_obj = ChartOfAccounts.objects.filter(id=account_id).first()
                if account_mapped_obj:
                    replace_account_list.append({
                        'account_mapped': account_mapped_obj,
                        'account_mapped_data': {
                            'id': str(account_mapped_obj.id),
                            'acc_code': account_mapped_obj.acc_code,
                            'acc_name': account_mapped_obj.acc_name,
                            'foreign_acc_name': account_mapped_obj.foreign_acc_name,
                        }
                    })
                else:
                    raise serializers.ValidationError({'account_mapped': _('Replace account mapped not found')})
            return replace_account_list
        raise serializers.ValidationError({'replace_account': _('Replace account length is not valid')})

    def update(self, instance, validated_data):
        replace_account = validated_data.pop('replace_account')
        bulk_info = []
        for item in replace_account:
            bulk_info.append(
                AccountDeterminationSub(account_determination=instance, **item)
            )
        instance.account_determination_sub.all().delete()
        AccountDeterminationSub.objects.bulk_create(bulk_info)
        instance.can_change_account = True
        instance.save(update_fields=['can_change_account'])
        return instance
