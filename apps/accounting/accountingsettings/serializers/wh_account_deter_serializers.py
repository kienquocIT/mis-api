from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.accounting.accountingsettings.models.wh_account_deter import WarehouseAccountDetermination


class WarehouseAccountDeterminationListSerializer(serializers.ModelSerializer):
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseAccountDetermination
        fields = (
            'id',
            'title',
            'warehouse_mapped_id',
            'account_number_list',
            'account_determination_type_convert'
        )

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return DEFAULT_ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class ProductTypeAccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseAccountDetermination
        fields = "__all__"
