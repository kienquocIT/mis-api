from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsTransfer
from apps.sales.inventory.serializers import GoodsTransferListSerializer, GoodsTransferCreateSerializer, \
    GoodsTransferDetailSerializer, GoodsTransferUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsTransferList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsTransfer.objects
    search_fields = ['title']
    serializer_list = GoodsTransferListSerializer
    serializer_create = GoodsTransferCreateSerializer
    serializer_detail = GoodsTransferDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT


    @swagger_auto_schema(
        operation_summary="Goods transfer List",
        operation_description="Get Goods transfer List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodstransfer', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods  transfer",
        operation_description="Create new Goods transfer",
        request_body=GoodsTransferCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodstransfer', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsTransferDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GoodsTransfer.objects
    serializer_detail = GoodsTransferDetailSerializer
    serializer_update = GoodsTransferUpdateSerializer
    detail_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Goods transfer detail",
        operation_description="Get Goods transfer detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodstransfer', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods transfer",
        operation_description="Update Goods transfer by ID",
        request_body=GoodsTransferUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodstransfer', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
