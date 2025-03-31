from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema

from apps.sales.asset.models import FixedAsset
from apps.sales.asset.serializers import FixedAssetListSerializer, FixedAssetCreateSerializer, \
    FixedAssetDetailSerializer, FixedAssetUpdateSerializer, AssetForLeaseListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ =[
    'FixedAssetList',
    'FixedAssetDetail',
    'AssetForLeaseList',
]

class FixedAssetList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = FixedAssetListSerializer
    serializer_create = FixedAssetCreateSerializer
    serializer_detail = FixedAssetDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        # get fixed assets that haven't been written off
        return super().get_queryset().filter(
            Q(fixed_asset_write_off__isnull=True) |
            Q(fixed_asset_write_off__isnull=False, fixed_asset_write_off__system_status=0)
        )

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


class FixedAssetDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = FixedAsset.objects
    serializer_detail = FixedAssetDetailSerializer
    serializer_update = FixedAssetUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Fixed Asset Detail",
        operation_description="Get Fixed Asset Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Fixed Asset Update",
        operation_description="Fixed Asset Update",
        request_body=FixedAssetUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='fixedasset', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)


class AssetForLeaseList(BaseListMixin, BaseCreateMixin):
    queryset = FixedAsset.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "status": ["exact"],
    }
    serializer_list = AssetForLeaseListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Fixed Asset For Lease List",
        operation_description="Get Fixed Asset For Lease List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='asset', model_code='fixedasset', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
