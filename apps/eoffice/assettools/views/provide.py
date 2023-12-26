__all__ = ['AssetToolsProvideRequestList']

from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.assettools.models import AssetToolsProvide
from apps.eoffice.assettools.serializers import AssetToolsProvideCreateSerializer, AssetToolsProvideListSerializer
from apps.shared import BaseCreateMixin, mask_view, BaseListMixin


class AssetToolsProvideRequestList(BaseListMixin, BaseCreateMixin):
    queryset = AssetToolsProvide.objects
    serializer_list = AssetToolsProvideListSerializer
    serializer_detail = AssetToolsProvideListSerializer
    serializer_create = AssetToolsProvideListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]
    search_fields = ('code', 'title')
    # filterset_class = BusinessTripListFilters

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit')
        #     .prefetch_related(
        #     'products',
        # )

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
