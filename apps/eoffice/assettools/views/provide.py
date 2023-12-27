__all__ = ['AssetToolsProvideRequestList', 'AssetToolsProvideRequestDetail']

from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.assettools.models import AssetToolsProvide
from apps.eoffice.assettools.serializers import AssetToolsProvideCreateSerializer, AssetToolsProvideListSerializer, \
    AssetToolsProvideDetailSerializer, AssetToolsProvideUpdateSerializer
from apps.shared import BaseCreateMixin, mask_view, BaseListMixin, BaseRetrieveMixin, BaseUpdateMixin


class AssetToolsProvideRequestList(BaseListMixin, BaseCreateMixin):
    queryset = AssetToolsProvide.objects
    serializer_list = AssetToolsProvideListSerializer
    serializer_detail = AssetToolsProvideListSerializer
    serializer_create = AssetToolsProvideCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]
    search_fields = ('code', 'title')

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit')

    @swagger_auto_schema(
        operation_summary="Asset, Tools Provide request list",
        operation_description="get provide request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsProvide', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Asset, Tools provide request",
        operation_description="Create asset tools provide request",
        request_body=AssetToolsProvideCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsProvide', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AssetToolsProvideRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AssetToolsProvide.objects
    serializer_detail = AssetToolsProvideDetailSerializer
    serializer_update = AssetToolsProvideUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit').prefetch_related(
            Prefetch(
                'asset_provide_map_product',
            )
        )

    @swagger_auto_schema(
        operation_summary="Asset provide detail",
        operation_description="get asset, tools provide request detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsProvide', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Asset provide update",
        operation_description="Asset, tools provide request update by ID",
        request_body=AssetToolsProvideUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsProvide', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
