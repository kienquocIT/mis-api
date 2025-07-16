from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Product
from apps.masterdata.saledata.models.product_warehouse import PWModified
from apps.sales.productmodificationbom.models import ProductModificationBOM
from apps.sales.productmodificationbom.serializers import (
    ProductModifiedListSerializer, ProductComponentListSerializer, ProductModificationBOMListSerializer,
    ProductModificationBOMCreateSerializer, ProductModificationBOMDetailSerializer,
    ProductModificationBOMUpdateSerializer, ProductModifiedBeforeListSerializer, LatestComponentListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


__all__ = [
    'ProductModificationBOMList',
    'ProductModificationBOMDetail',
    'PMBOMProductModifiedList',
    'PMBOMProductComponentList',
    'PMBOMProductModifiedBeforeList',
    'PMBOMLatestComponentList'
]

# main
class ProductModificationBOMList(BaseListMixin, BaseCreateMixin):
    queryset = ProductModificationBOM.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ProductModificationBOMListSerializer
    serializer_create = ProductModificationBOMCreateSerializer
    serializer_detail = ProductModificationBOMDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related('employee_created__group')

    @swagger_auto_schema(
        operation_summary="Product Modification BOM list",
        operation_description="Product Modification BOM list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodificationbom', model_code='productmodificationbom', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Product Modification BOM",
        operation_description="Create new Product Modification BOM",
        request_body=ProductModificationBOMCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodificationbom', model_code='productmodificationbom', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductModificationBOMDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProductModificationBOM.objects  # noqa
    serializer_detail = ProductModificationBOMDetailSerializer
    serializer_update = ProductModificationBOMUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'current_components',
            'added_components'
        ).select_related()

    @swagger_auto_schema(operation_summary='Detail Product Modification BOM')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodificationbom', model_code='productmodificationbom', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Product Modification BOM", request_body=ProductModificationBOMUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='productmodificationbom', model_code='productmodificationbom', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

# related
class PMBOMProductModifiedList(BaseListMixin):
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


class PMBOMProductModifiedBeforeList(BaseListMixin):
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


class PMBOMProductComponentList(BaseListMixin):
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


class PMBOMLatestComponentList(BaseListMixin):
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
