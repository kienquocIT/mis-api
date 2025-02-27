from drf_yasg.utils import swagger_auto_schema

from apps.sales.asset.models import FixedAsset, FixedAssetWriteOff
from apps.sales.asset.serializers import FixedAssetListSerializer, FixedAssetCreateSerializer, \
    FixedAssetDetailSerializer, FixedAssetUpdateSerializer, FixedAssetWriteOffListSerializer, \
    FixedAssetWriteOffCreateSerializer, FixedAssetWriteOffDetailSerializer, FixedAssetWriteOffUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ =[
    'FixedAssetWriteOffList',
    'FixedAssetWriteOffDetail'
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
        operation_summary="Fixed Asset Writeoff List",
        operation_description="Get Fixed Asset Writeoff List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedassetwriteoff', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Fixed Asset Writeoff",
        operation_description="Create New Fixed Asset Writeoff",
        request_body=FixedAssetWriteOffCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='asset', model_code='fixedassetwriteoff', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class FixedAssetWriteOffDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = FixedAssetWriteOff.objects
    serializer_detail = FixedAssetWriteOffDetailSerializer
    serializer_update = FixedAssetWriteOffUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Fixed Asset Writeoff Detail",
        operation_description="Get Fixed Asset Writeoff Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedassetwriteoff', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Fixed Asset Writeoff Update",
        operation_description="Fixed Asset Writeoff Update",
        request_body=FixedAssetWriteOffUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedassetwriteoff', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'fixed_asset_write_off_id': pk,
            'user': request.user
        }
        return self.update(request, *args, pk, **kwargs)