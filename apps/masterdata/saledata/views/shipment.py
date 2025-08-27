from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models.shipment import ContainerTypeInfo
from apps.masterdata.saledata.serializers.shipment import ContainerListSerializer, ContainerCreateSerializer, \
    ContainerDetailSerializer, ContainerUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin


class ContainerMasterDataList(BaseListMixin, BaseCreateMixin):
    queryset = ContainerTypeInfo.objects
    serializer_list = ContainerListSerializer
    serializer_create = ContainerCreateSerializer
    serializer_detail = ContainerDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="Container type request list",
        operation_description="get container type request list"
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create container type",
        operation_description="Create new container type"
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContainerMasterDataDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ContainerTypeInfo.objects
    serializer_detail = ContainerDetailSerializer
    serializer_update = ContainerUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Shift Detail')
    @mask_view(
        login_require=True,
        auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Update Shift')
    @mask_view(
        login_require=True,
        auth_require=False,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
