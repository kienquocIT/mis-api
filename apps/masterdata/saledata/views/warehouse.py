from drf_yasg.utils import swagger_auto_schema

from apps.shared import (
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin, mask_view,
)
from apps.masterdata.saledata.models import (
    WareHouse, WareHouseStock, ProductWareHouse
)
from apps.masterdata.saledata.serializers import (
    WareHouseListSerializer, WareHouseCreateSerializer,
    WareHouseDetailSerializer, WareHouseUpdateSerializer, WarehouseStockListSerializer,
    ProductWareHouseStockListSerializer, ProductWareHouseListSerializer
)

__all__ = [
    'WareHouseList', 'WareHouseDetail', 'WarehouseStockList',
    'WareHouseCheckAvailableProductList', 'ProductWareHouseList'
]


class WareHouseList(BaseListMixin, BaseCreateMixin):
    queryset = WareHouse.objects
    serializer_list = WareHouseListSerializer
    serializer_create = WareHouseCreateSerializer
    serializer_detail = WareHouseDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    search_fields = ("title", "code",)
    filterset_fields = {
        "is_active": ['exact'],
    }

    def get_queryset(self):
        return super().get_queryset().prefetch_related('warehouse_stock_warehouse')

    @swagger_auto_schema(operation_summary='WareHouse List')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Create new WareHouse', request_body=WareHouseCreateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WareHouseDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = WareHouse.objects
    serializer_detail = WareHouseDetailSerializer
    serializer_update = WareHouseUpdateSerializer

    @swagger_auto_schema(operation_summary='Detail a warehouse')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Update a warehouse', request_body=WareHouseUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Destroy a warehouse')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class WarehouseStockList(BaseListMixin):
    queryset = WareHouseStock.objects
    serializer_list = WarehouseStockListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = {
        "product": ['exact', 'in'],
        "warehouse": ['exact', 'in'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related('product', 'warehouse')

    @swagger_auto_schema(operation_summary='WareHouse stock product')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WareHouseCheckAvailableProductList(BaseListMixin):
    queryset = WareHouse.objects
    serializer_list = ProductWareHouseStockListSerializer
    list_hidden_field = ['tenant_id', 'product_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, product_id, uom_id, **kwargs):
        self.ser_context = {
            'product_id': product_id,
            'uom_id': uom_id,
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.list(request, *args, **kwargs)


class ProductWareHouseList(BaseListMixin):
    queryset = ProductWareHouse.objects
    serializer_list = ProductWareHouseListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('product', 'warehouse')

    @swagger_auto_schema(operation_summary='Product WareHouse')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
