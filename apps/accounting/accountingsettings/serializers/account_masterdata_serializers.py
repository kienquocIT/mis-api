from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import (
    ChartOfAccounts, DefaultAccountDetermination, DefaultAccountDeterminationSub,
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
            'foreign_title',
            'account_mapped',
            'default_account_determination_type',
            'default_account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_mapped(cls, obj):
        return [item.account_mapped_data for item in obj.default_acc_deter_sub.all()]

    @classmethod
    def get_default_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.default_account_determination_type][1]


class DefaultAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultAccountDetermination
        fields = "__all__"


class DefaultAccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    replace_account = serializers.JSONField(default=list)

    class Meta:
        model = DefaultAccountDetermination
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
                DefaultAccountDeterminationSub(default_acc_deter=instance, **item)
            )
        instance.default_acc_deter_sub.all().delete()
        DefaultAccountDeterminationSub.objects.bulk_create(bulk_info)
        instance.is_changed = True
        instance.save(update_fields=['is_changed'])
        return instance
