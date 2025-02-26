from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.accounting.accountingsettings.models.prd_account_deter import ProductAccountDetermination


class ProductAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_mapped = serializers.SerializerMethodField()
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = ProductAccountDetermination
        fields = (
            'id',
            'title',
            'product_mapped_id',
            'account_mapped',
            'account_determination_type',
            'account_determination_type_convert'
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
    def get_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class ProductAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAccountDetermination
        fields = "__all__"
