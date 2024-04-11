from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.serializers.warehouse import ProductWarehouseLotListSerializer, \
    ProductWarehouseSerialListSerializer, ProductWarehouseAssetToolsListSerializer
from apps.shared import (
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin, mask_view,
)
from apps.masterdata.saledata.models import (
    WareHouse, ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial, WarehouseEmployeeConfig
)
from apps.masterdata.saledata.serializers import (
    WareHouseListSerializer, WareHouseCreateSerializer, WareHouseListSerializerForInventoryAdjustment,
    WareHouseDetailSerializer, WareHouseUpdateSerializer,
    ProductWareHouseStockListSerializer, ProductWareHouseListSerializer,
    WarehouseEmployeeConfigListSerializer, WarehouseEmployeeConfigCreateSerializer,
    WarehouseEmployeeConfigDetailSerializer
)
from ..filters import ProductWareHouseListFilter

__all__ = [
    'WareHouseList', 'WareHouseDetail', 'WareHouseCheckAvailableProductList', 'ProductWareHouseList',
    'WareHouseListForInventoryAdjustment', 'ProductWareHouseAssetToolsList'
]


class WareHouseList(BaseListMixin, BaseCreateMixin):
    queryset = WareHouse.objects
    serializer_list = WareHouseListSerializer
    serializer_create = WareHouseCreateSerializer
    serializer_detail = WareHouseDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    search_fields = ("title", "code",)
    filterset_fields = {
        "is_active": ['exact'],
        "is_dropship": ['exact'],
    }

    def get_queryset(self):
        if 'interact' in self.request.query_params:
            interact = WarehouseEmployeeConfig.objects.filter(employee=self.request.user.employee_current_id).first()
            if interact:
                return super().get_queryset().filter(id__in=interact.warehouse_list).order_by('code')
        return super().get_queryset()

    @swagger_auto_schema(operation_summary='WareHouse List')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Create new WareHouse', request_body=WareHouseCreateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WareHouseDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = WareHouse.objects
    serializer_detail = WareHouseDetailSerializer
    serializer_update = WareHouseUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail a warehouse')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Update a warehouse', request_body=WareHouseUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Destroy a warehouse')
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)


class WareHouseCheckAvailableProductList(BaseListMixin):
    queryset = WareHouse.objects
    serializer_list = ProductWareHouseStockListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @property
    def filter_kwargs(self) -> dict[str, any]:
        return {
            **self.cls_check.attr.setup_hidden(from_view='list'),
        }

    @swagger_auto_schema()
    @mask_view(
        login_require=True, auth_require=False,
    )
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
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_class = ProductWareHouseListFilter

    # filterset_fields = {
    #     "product_id": ["exact"],
    #     "warehouse_id": ["exact"],
    # }

    def get_queryset(self):
        if 'interact' in self.request.query_params:
            interact = WarehouseEmployeeConfig.objects.filter(employee=self.request.user.employee_current_id).first()
            if interact:
                return super().get_queryset().select_related(
                    'product', 'warehouse', 'uom'
                ).filter(warehouse_id__in=interact.warehouse_list).order_by('product__code')
        return super().get_queryset().select_related(
            'product', 'warehouse', 'uom',
        ).order_by('product__code')

    @swagger_auto_schema(operation_summary='Product WareHouse')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WareHouseListForInventoryAdjustment(BaseListMixin):
    queryset = WareHouse.objects
    serializer_list = WareHouseListSerializerForInventoryAdjustment
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    search_fields = ("title", "code",)
    filterset_fields = {
        "is_active": ['exact'],
    }

    @swagger_auto_schema(operation_summary='WareHouse List')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductWareHouseLotList(BaseListMixin):
    queryset = ProductWareHouseLot.objects
    search_fields = ['lot_number', ]
    filterset_fields = {
        "product_warehouse_id": ["exact"],
        "product_warehouse__product_id": ["exact"],
        "product_warehouse__warehouse_id": ["exact"],
        "lot_number": ["exact"],
    }
    serializer_list = ProductWarehouseLotListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product_warehouse__product',
            'product_warehouse__product__inventory_uom',
            'product_warehouse__warehouse',
            'product_warehouse__uom',
        )

    @swagger_auto_schema(operation_summary='Product WareHouse Lot')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductWareHouseSerialList(BaseListMixin):
    queryset = ProductWareHouseSerial.objects
    search_fields = ['vendor_serial_number', 'serial_number']
    filterset_fields = {
        "product_warehouse_id": ["exact"],
        "product_warehouse__product_id": ["exact"],
        "product_warehouse__warehouse_id": ["exact"],
        "serial_number": ["exact"],
        "is_delete": ["exact"],
    }
    serializer_list = ProductWarehouseSerialListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product_warehouse__product',
            'product_warehouse__warehouse',
        )

    @swagger_auto_schema(operation_summary='Product WareHouse Serial')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductWareHouseAssetToolsList(BaseListMixin):
    queryset = ProductWareHouse.objects
    serializer_list = ProductWarehouseAssetToolsListSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_class = ProductWareHouseListFilter

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product',
            'uom',
            'warehouse',
        )

    @swagger_auto_schema(operation_summary='Product Asset list')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WarehouseEmployeeConfigList(BaseListMixin, BaseCreateMixin):
    queryset = WarehouseEmployeeConfig.objects
    serializer_list = WarehouseEmployeeConfigListSerializer
    serializer_create = WarehouseEmployeeConfigCreateSerializer
    serializer_detail = WarehouseEmployeeConfigDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('employee').prefetch_related('wh_emp_config_detail_cf')

    @swagger_auto_schema(operation_summary='Warehouse Employee Config List')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create new Warehouse Employee Config',
        request_body=WarehouseEmployeeConfigCreateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WarehouseEmployeeConfigDetail(BaseRetrieveMixin, BaseDestroyMixin):
    queryset = WarehouseEmployeeConfig.objects
    serializer_detail = WarehouseEmployeeConfigDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail a warehouse-employee')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Destroy a warehouse-employee')
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)
