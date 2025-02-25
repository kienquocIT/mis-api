from drf_yasg.utils import swagger_auto_schema

from apps.sales.asset.models import FixedAsset, FixedAssetWriteOff
from apps.sales.asset.serializers import FixedAssetListSerializer, FixedAssetCreateSerializer, \
    FixedAssetDetailSerializer, FixedAssetUpdateSerializer, FixedAssetWriteOffListSerializer, \
    FixedAssetWriteOffCreateSerializer, FixedAssetWriteOffDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ =[
    'FixedAssetWriteOffList',
]

class FixedAssetWriteOffList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAssetWriteOff.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = FixedAssetWriteOffListSerializer
    serializer_create = FixedAssetWriteOffCreateSerializer
    serializer_detail = FixedAssetWriteOffDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Fixed Asset List",
        operation_description="Get Fixed Asset List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Fixed Asset",
        operation_description="Create New Fixed Asset",
        request_body=FixedAssetCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='asset', model_code='fixedasset', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)
