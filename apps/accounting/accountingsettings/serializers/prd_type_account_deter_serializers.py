from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.accounting.accountingsettings.models.prd_type_account_deter import ProductTypeAccountDetermination


class ProductTypeAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = ProductTypeAccountDetermination
        fields = (
            'id',
            'title',
            'product_type_mapped_id',
            'account_number_list',
            'account_determination_type_convert'
        )

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class ProductTypeAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTypeAccountDetermination
        fields = "__all__"
