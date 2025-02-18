from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import FixedAssetClassification, FixedAssetClassificationGroup, ToolClassification
from apps.masterdata.saledata.serializers import FixedAssetClassificationListSerializer, \
    FixedAssetClassificationGroupListSerializer, ToolClassificationUpdateSerializer
from apps.masterdata.saledata.serializers.asset import ToolClassificationListSerializer, \
    ToolClassificationCreateSerializer, ToolClassificationDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ = [
    'FixedAssetClassificationGroupList',
    'FixedAssetClassificationList',
    'ToolClassificationList'
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


class ToolClassificationList(BaseListMixin, BaseCreateMixin):
    queryset = ToolClassification.objects
    serializer_list = ToolClassificationListSerializer
    serializer_create = ToolClassificationCreateSerializer
    serializer_detail = ToolClassificationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="ToolClassification list",
        operation_description="ToolClassification list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ToolClassification create",
        operation_description="ToolClassification create",
        request_body=ToolClassificationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require = False
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ToolClassificationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ToolClassification.objects
    search_fields = ['title']
    filterset_fields = {}
    serializer_update = ToolClassificationUpdateSerializer
    serializer_detail = ToolClassificationDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Tool Classification')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update Tool Classification", request_body=ToolClassificationUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
