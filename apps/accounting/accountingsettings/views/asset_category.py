from drf_yasg.utils import swagger_auto_schema

from apps.accounting.accountingsettings.models import AssetCategory
from apps.accounting.accountingsettings.serializers import AssetCategoryListSerializer, AssetCategoryCreateSerializer, \
    AssetCategoryDetailSerializer, AssetCategoryUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, BaseUpdateMixin, mask_view, BaseRetrieveMixin

# Create your views here.
class AssetCategoryList(BaseListMixin, BaseCreateMixin):
    queryset = AssetCategory.objects
    serializer_list = AssetCategoryListSerializer
    serializer_create = AssetCategoryCreateSerializer
    serializer_detail = AssetCategoryDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Asset Category List",
        operation_description="Get Asset Category List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Dimension Definition Create",
        operation_description="Create new Dimension Definition",
        request_body=AssetCategoryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AssetCategoryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AssetCategory.objects
    serializer_detail = AssetCategoryDetailSerializer
    serializer_update = AssetCategoryUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Asset Category Detail",
        operation_description="Get Asset Category Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(request_body=AssetCategoryUpdateSerializer)
    @mask_view(login_require=True, auth_require=True,
               allow_admin_tenant=True, allow_admin_company=True,
               )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
