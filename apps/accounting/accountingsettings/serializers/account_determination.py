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
    account_determination_sub_list= serializers.SerializerMethodField()
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = AccountDetermination
        fields = (
            'id',
            'code',
            'title',
            'foreign_title',
            'transaction_key',
            'description',
            'example',
            'account_determination_sub_list',
            'account_determination_type',
            'account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_determination_sub_list(cls, obj):
        return [item.account_mapped_data for item in obj.sub_items.all()]

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class AccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetermination
        fields = "__all__"


class AccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    replace_account_list = serializers.JSONField(default=list)

    class Meta:
        model = AccountDetermination
        fields = (
            'replace_account_list',
        )

    @classmethod
    def validate_replace_account_list(cls, replace_account_list):
        if len(replace_account_list) != 0:
            valid_replace_account_list = []
            for account_id in replace_account_list:
                account_mapped_obj = ChartOfAccounts.objects.filter(id=account_id).first()
                if account_mapped_obj:
                    valid_replace_account_list.append({
                        'transaction_key_sub': '', # must fill
                        'description': '',
                        'account_mapped': account_mapped_obj,
                        'account_mapped_data': {
                            'id': str(account_mapped_obj.id),
                            'acc_code': account_mapped_obj.acc_code,
                            'acc_name': account_mapped_obj.acc_name,
                            'foreign_acc_name': account_mapped_obj.foreign_acc_name,
                        },
                        'match_context': {}, # must fill
                        'search_rule': '', # must fill
                        'priority': 0
                    })
                else:
                    raise serializers.ValidationError({'account_mapped': _('Account mapped not found')})
            return valid_replace_account_list
        raise serializers.ValidationError({'replace_account': _('Account list cannot empty')})

    def validate(self, validate_data):
        if not self.instance.can_change_account:
            raise serializers.ValidationError({'err': _('Not allowed to change this account determination')})
        return validate_data

    def update(self, instance, validated_data):
        replace_account_list = validated_data.pop('replace_account_list', [])
        bulk_info = []
        for item in replace_account_list:
            bulk_info.append(
                AccountDeterminationSub(account_determination=instance, **item)
            )
        instance.sub_items.all().delete()
        AccountDeterminationSub.objects.bulk_create(bulk_info)
        instance.can_change_account = True
        instance.save(update_fields=['can_change_account'])
        return instance
