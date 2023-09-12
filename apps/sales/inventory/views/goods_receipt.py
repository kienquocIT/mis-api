from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsReceipt
from apps.sales.inventory.serializers.goods_receipt import GoodsReceiptListSerializer, GoodsReceiptCreateSerializer, \
    GoodsReceiptUpdateSerializer, GoodsReceiptDetailSerializer
from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderQuotation, PurchaseOrderProduct
from apps.sales.purchasing.serializers.purchase_order import PurchaseOrderCreateSerializer, \
    PurchaseOrderListSerializer, PurchaseOrderUpdateSerializer, PurchaseOrderDetailSerializer, \
    PurchaseOrderProductListSerializer, PurchaseOrderSaleListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsReceiptList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = GoodsReceipt.objects
    filterset_fields = {
        'purchase_order_id': ['exact'],
    }
    serializer_list = GoodsReceiptListSerializer
    serializer_create = GoodsReceiptCreateSerializer
    serializer_detail = GoodsReceiptListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "purchase_order",
        )

    @swagger_auto_schema(
        operation_summary="Goods receipt List",
        operation_description="Get Goods receipt List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='purchasing', model_code='purchaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods receipt",
        operation_description="Create new Goods receipt",
        request_body=PurchaseOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='purchasing', model_code='purchaseorder', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsReceiptDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = GoodsReceipt.objects
    serializer_detail = GoodsReceiptDetailSerializer
    serializer_update = GoodsReceiptUpdateSerializer
    update_hidden_field = ['employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "supplier",
        ).prefetch_related(
            'purchase_requests',
        )

    @swagger_auto_schema(
        operation_summary="Goods receipt order detail",
        operation_description="Get Goods receipt detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='purchasing', model_code='purchaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods receipt",
        operation_description="Update Goods receipt by ID",
        request_body=GoodsReceiptUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='purchasing', model_code='purchaseorder', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)