from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import ProductWareHouse
from apps.sales.inventory.models import GoodsReceipt
from apps.sales.inventory.serializers.goods_detail import (
    GoodsDetailListSerializer, GoodsDetailDataCreateSerializer, GoodsDetailDataDetailSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class GoodsDetailList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsReceipt.objects
    serializer_list = GoodsDetailListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'employee_inherit',
        ).prefetch_related(
            'goods_receipt_product_goods_receipt__goods_receipt_warehouse_gr_product__warehouse',
            'goods_receipt_product_goods_receipt__product',
            'product_wh_serial_goods_receipt',
            'product_wh_lot_goods_receipt'
        )

    @swagger_auto_schema(
        operation_summary="Goods detail List",
        operation_description="Get Goods detail List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsdetail', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GoodsDetailDataList(BaseCreateMixin):
    queryset = ProductWareHouse.objects
    serializer_create = GoodsDetailDataCreateSerializer
    serializer_detail = GoodsDetailDataDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Create Goods Detail Product Warehouse",
        operation_description="Create new Goods Detail Product Warehouse",
        request_body=GoodsDetailDataCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsdetail', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
