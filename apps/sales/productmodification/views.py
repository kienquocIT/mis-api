from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import ProductWareHouse, Product, ProductWareHouseSerial, ProductWareHouseLot
from apps.masterdata.saledata.models.product_warehouse import PWModified
from apps.sales.productmodification.models import ProductModification, RemovedComponent
from apps.sales.productmodification.serializers import (
    WarehouseListByProductSerializer, ProductModifiedListSerializer,
    ProductComponentListSerializer, ProductSerialListSerializer, ProductModificationListSerializer,
    ProductModificationCreateSerializer, ProductModificationDetailSerializer, ProductModificationUpdateSerializer,
    ProductLotListSerializer, ProductModificationDDListSerializer, ProductModificationProductGRListSerializer,
    ProductModifiedBeforeListSerializer, LatestComponentListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ = [
    'ProductModificationList',
    'ProductModificationDetail',
    'ProductModifiedList',
    'ProductComponentList',
    'WarehouseListByProduct',
    'ProductSerialList',
    'ProductLotList',
    'ProductModificationDDList',
    'ProductModificationProductGRList',
]

# main
class ProductModificationList(BaseListMixin, BaseCreateMixin):
    queryset = ProductModification.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ProductModificationListSerializer
    serializer_create = ProductModificationCreateSerializer
    serializer_detail = ProductModificationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related('employee_created__group')

    @swagger_auto_schema(
        operation_summary="Product Modification list",
        operation_description="Product Modification list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodification', model_code='productmodification', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Product Modification",
        operation_description="Create new Product Modification",
        request_body=ProductModificationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodification', model_code='productmodification', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductModificationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProductModification.objects  # noqa
    serializer_detail = ProductModificationDetailSerializer
    serializer_update = ProductModificationUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'current_components',
            'current_components__current_components_detail',
        ).select_related()

    @swagger_auto_schema(operation_summary='Detail Product Modification')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodification', model_code='productmodification', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Product Modification", request_body=ProductModificationUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodification', model_code='productmodification', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

# related
class ProductModifiedList(BaseListMixin):
    queryset = Product.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ProductModifiedListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(general_product_types_mapped__is_service=False)

    @swagger_auto_schema(
        operation_summary="Product Modified List",
        operation_description="Product Modified List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductModifiedBeforeList(BaseListMixin):
    queryset = PWModified.objects
    search_fields = [
        'modified_number',
    ]
    serializer_list = ProductModifiedBeforeListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'product_warehouse', 'product_warehouse__product', 'product_warehouse_serial', 'product_warehouse_lot'
        )

    @swagger_auto_schema(
        operation_summary="Product Modified Before List",
        operation_description="Product Modified Before List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductComponentList(BaseListMixin):
    queryset = Product.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'id': ['exact'],
    }
    serializer_list = ProductComponentListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(general_product_types_mapped__is_service=False)

    @swagger_auto_schema(
        operation_summary="Product Component List",
        operation_description="Product Component List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LatestComponentList(BaseListMixin):
    queryset = PWModified.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'product_warehouse__product_id': ['exact'],
        'modified_number': ['exact'],
    }
    serializer_list = LatestComponentListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'pw_modified_components',
            'pw_modified_components__pw_modified_component_detail'
        )

    @swagger_auto_schema(
        operation_summary="Latest Component List",
        operation_description="Latest Component List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WarehouseListByProduct(BaseListMixin):
    queryset = ProductWareHouse.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'product_id': ['exact'],
    }
    serializer_list = WarehouseListByProductSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    # def get_queryset(self):
    #     return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="Warehouse List By Product",
        operation_description="Warehouse List By Product",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductLotList(BaseListMixin):
    queryset = ProductWareHouseLot.objects
    search_fields = [
        'lot_number',
    ]
    filterset_fields = {
        'product_warehouse__product_id': ['exact'],
        'product_warehouse__warehouse_id': ['exact'],
    }
    serializer_list = ProductLotListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    # def get_queryset(self):
    #     return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="Product Lot List",
        operation_description="Product Lot List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductSerialList(BaseListMixin):
    queryset = ProductWareHouseSerial.objects
    search_fields = [
        'vendor_serial_number',
        'serial_number',
    ]
    filterset_fields = {
        'product_warehouse__product_id': ['exact'],
        'product_warehouse__warehouse_id': ['exact'],
    }
    serializer_list = ProductSerialListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(serial_status=0)

    @swagger_auto_schema(
        operation_summary="Product Serial List",
        operation_description="Product Serial List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductModificationDDList(BaseListMixin):
    queryset = ProductModification.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'created_goods_receipt': ['exact'],
    }
    serializer_list = ProductModificationDDListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Product Modification DD List",
        operation_description="Get Product Modification DD List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# VIEWS USE FOR GOODS RECEIPT
class ProductModificationProductGRList(BaseListMixin):
    queryset = RemovedComponent.objects
    filterset_fields = {
        'product_modified_id': ['in', 'exact'],
    }
    serializer_list = ProductModificationProductGRListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().filter(gr_remain_quantity__gt=0).select_related(
            'component_product',
        )

    @swagger_auto_schema(
        operation_summary="Product Modification Product GR List",
        operation_description="Get Product Modification Product GR List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
