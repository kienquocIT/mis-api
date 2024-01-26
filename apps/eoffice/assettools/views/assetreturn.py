__all__ = ['AssetToolsReturnList', 'AssetToolsReturnDetail']

from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.assettools.models import AssetToolsReturn
from apps.eoffice.assettools.serializers import AssetToolsReturnListSerializer, AssetToolsReturnCreateSerializer, \
    AssetToolsReturnDetailSerializer, AssetToolsReturnUpdateSerializer
from apps.shared import BaseCreateMixin, mask_view, BaseListMixin, BaseRetrieveMixin, BaseUpdateMixin


class AssetToolsReturnList(BaseListMixin, BaseCreateMixin):
    queryset = AssetToolsReturn.objects
    serializer_list = AssetToolsReturnListSerializer
    serializer_create = AssetToolsReturnCreateSerializer
    serializer_detail = AssetToolsReturnDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related('employee_created')

    @swagger_auto_schema(
        operation_summary="Asset, Tools Return request list",
        operation_description="get asset return request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsReturn', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Asset return request",
        operation_description="Create asset return request",
        request_body=AssetToolsReturnCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsReturn', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class AssetToolsReturnDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AssetToolsReturn.objects
    serializer_detail = AssetToolsReturnDetailSerializer
    serializer_update = AssetToolsReturnUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Asset return detail",
        operation_description="get asset, tools return request detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsReturn', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Asset return update",
        operation_description="Asset, tools return request update by ID",
        request_body=AssetToolsReturnUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='assetTools', model_code='AssetToolsReturn', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
