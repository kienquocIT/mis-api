from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import (
    DEFAULT_ACCOUNT_DETERMINATION_TYPE,
    ChartOfAccounts
)
from apps.accounting.accountingsettings.models.prd_type_account_deter import ProductTypeAccountDetermination, \
    ProductTypeAccountDeterminationSub


class ProductTypeAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_mapped = serializers.SerializerMethodField()
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = ProductTypeAccountDetermination
        fields = (
            'id',
            'title',
            'foreign_title',
            'product_type_mapped_id',
            'account_mapped',
            'account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_mapped(cls, obj):
        return [item.account_mapped_data for item in obj.prd_type_account_deter_sub.all()]

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class ProductTypeAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTypeAccountDetermination
        fields = "__all__"


class ProductTypeAccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    replace_account = serializers.JSONField(default=list)

    class Meta:
        model = ProductTypeAccountDetermination
        fields = (
            'replace_account',
        )

    @classmethod
    def validate_replace_account(cls, replace_account):
        if len(replace_account) == 1:
            replace_account_list = []
            for account_id in replace_account:
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
                ProductTypeAccountDeterminationSub(prd_type_account_deter=instance, **item)
            )
        instance.prd_type_account_deter_sub.all().delete()
        ProductTypeAccountDeterminationSub.objects.bulk_create(bulk_info)
        instance.is_changed = True
        instance.save(update_fields=['is_changed'])
        return instance
