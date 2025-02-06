from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import FixedAssetClassification, FixedAssetClassificationGroup
from apps.masterdata.saledata.serializers import FixedAssetClassificationListSerializer, \
    FixedAssetClassificationGroupListSerializer
from apps.shared import BaseListMixin, mask_view

__all__ = [
    'FixedAssetClassificationGroupList',
    'FixedAssetClassificationList',
]

class FixedAssetClassificationGroupList(BaseListMixin):
    queryset = FixedAssetClassificationGroup.objects
    serializer_list = FixedAssetClassificationGroupListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="FixedAssetClassificationGroup list",
        operation_description="FixedAssetClassificationGroup list",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FixedAssetClassificationList(BaseListMixin):
    queryset = FixedAssetClassification.objects
    serializer_list = FixedAssetClassificationListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="FixedAssetClassification list",
        operation_description="FixedAssetClassification list",
    )
    @mask_view(
        login_require=True, auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
