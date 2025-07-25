from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial
from apps.sales.inventory.models import GoodsDetail, GoodsReceipt
from apps.sales.inventory.serializers.goods_detail import (
    GoodsDetailListSerializer, GoodsDetailDataCreateSerializer, GoodsDetailDataDetailSerializer,
    GoodsDetailCreateSerializerImportDB, GoodsDetailDetailSerializerImportDB, GoodsDetailSerialDataSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class GoodsDetailList(BaseListMixin):
    queryset = GoodsDetail.objects
    search_fields = [
        'product__code',
        'product__title',
        'warehouse__code',
        'warehouse__title',
        'goods_receipt__code',
        'goods_receipt__title',
        'purchase_request__code',
        'purchase_request__title',
        'lot__lot_number',
        'date_created',
        'employee_inherit__first_name',
        'employee_inherit__last_name',
    ]
    serializer_list = GoodsDetailListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

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


class GoodsDetailSerialDataList(BaseListMixin):
    queryset = ProductWareHouseSerial.objects
    serializer_list = GoodsDetailSerialDataSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        warehouse_id = self.request.query_params.get('warehouse_id')
        goods_receipt_id = self.request.query_params.get('goods_receipt_id')
        purchase_request_id = self.request.query_params.get('purchase_request_id')

        queryset = super().get_queryset().filter(
            product_warehouse__product_id=product_id,
            product_warehouse__warehouse_id=warehouse_id,
            goods_receipt_id=goods_receipt_id,
            purchase_request_id=purchase_request_id
        ).select_related().prefetch_related().order_by('date_created')
        if queryset.count() == 0:
            gr_obj = GoodsReceipt.objects.filter_on_company(id=goods_receipt_id).first()
            if gr_obj:
                serial_mapped = gr_obj.goods_receipt_serial_goods_receipt.first()
                if serial_mapped:
                    return super().get_queryset().filter(serial_number=serial_mapped.serial_number)
        return queryset

    @swagger_auto_schema(
        operation_summary="Goods detail Serial data List",
        operation_description="Get Goods detail Serial data List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsdetail', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
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


class GoodsDetailListImportDB(BaseCreateMixin):
    queryset = ProductWareHouse.objects
    serializer_create = GoodsDetailCreateSerializerImportDB
    serializer_detail = GoodsDetailDetailSerializerImportDB
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Goods Detail List Import DB",
        operation_description="Goods Detail List Import DB",
        request_body=GoodsDetailCreateSerializerImportDB,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsdetail', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
