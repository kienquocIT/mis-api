from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsReceipt
from apps.sales.inventory.serializers.goods_receipt import GoodsReceiptListSerializer, GoodsReceiptCreateSerializer, \
    GoodsReceiptUpdateSerializer, GoodsReceiptDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsReceiptList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = GoodsReceipt.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'purchase_order_id': ['exact'],
    }
    serializer_list = GoodsReceiptListSerializer
    serializer_create = GoodsReceiptCreateSerializer
    serializer_detail = GoodsReceiptListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return self.get_queryset_custom_direct_page()

    @swagger_auto_schema(
        operation_summary="Goods receipt List",
        operation_description="Get Goods receipt List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreceipt', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods receipt",
        operation_description="Create new Goods receipt",
        request_body=GoodsReceiptCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreceipt', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class GoodsReceiptDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = GoodsReceipt.objects
    serializer_detail = GoodsReceiptDetailSerializer
    serializer_update = GoodsReceiptUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit').prefetch_related('purchase_requests',)

    @swagger_auto_schema(
        operation_summary="Goods receipt detail",
        operation_description="Get Goods receipt detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreceipt', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods receipt",
        operation_description="Update Goods receipt by ID",
        request_body=GoodsReceiptUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreceipt', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)
