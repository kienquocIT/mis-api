__all__ = ['AssetToolsDeliveryRequestList', 'AssetToolsProductUsedList']

from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.assettools.models import AssetToolsDelivery, ProductDeliveredMapProvide
from apps.eoffice.assettools.serializers import AssetToolsDeliveryCreateSerializer, AssetToolsDeliveryDetailSerializer,\
    AssetToolsProductUsedListSerializer, AssetToolsDeliveryListSerializer
from apps.shared import BaseCreateMixin, mask_view, BaseListMixin


class AssetToolsDeliveryRequestList(BaseListMixin, BaseCreateMixin):
    queryset = AssetToolsDelivery.objects
    serializer_list = AssetToolsDeliveryListSerializer
    serializer_create = AssetToolsDeliveryCreateSerializer
    serializer_detail = AssetToolsDeliveryDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    # def get_queryset(self):
    #     return super().get_queryset().prefetch_related(
    #         Prefetch(
    #             'provide_map_delivery',
    #         )
    #     )

    @swagger_auto_schema(
        operation_summary="Asset, Tools Delivery request list",
        operation_description="get delivery request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsDelivery', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Asset, Tools provide request",
        operation_description="Create asset tools provide request",
        request_body=AssetToolsDeliveryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsDelivery', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class AssetToolsProductUsedList(BaseListMixin):
    queryset = ProductDeliveredMapProvide.objects
    serializer_list = AssetToolsProductUsedListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = ('code', 'title')

    def get_queryset(self):
        return super().get_queryset().select_related('product')

    @swagger_auto_schema(
        operation_summary="Asset, Tools Provide request list",
        operation_description="get provide request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsDelivery', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
