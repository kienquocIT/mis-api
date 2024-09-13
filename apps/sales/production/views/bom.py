from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Product, Expense
from apps.sales.production.models import BOM
from apps.sales.production.serializers.bom import (
    BOMProductMaterialListSerializer, LaborListForBOMSerializer,
    BOMUpdateSerializer, BOMDetailSerializer, BOMCreateSerializer, BOMListSerializer, BOMOrderListSerializer,
    FinishProductForBOMSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ProductListForBOM(BaseListMixin):
    queryset = Product.objects
    search_fields = ['title']
    filterset_fields = {
        'general_product_types_mapped__is_finished_goods': ['exact'],
        'general_product_types_mapped__is_service': ['exact'],
    }
    serializer_list = FinishProductForBOMSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(has_bom=False).select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Finish Product List For BOM",
        operation_description="Finish Product List For BOM",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LaborListForBOM(BaseListMixin):
    queryset = Expense.objects
    search_fields = ['title']
    serializer_list = LaborListForBOMSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('uom').prefetch_related(
            'expense__uom', 'expense__price'
        )

    @swagger_auto_schema(
        operation_summary="Product Material List For BOM",
        operation_description="Product Material List For BOM",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductMaterialListForBOM(BaseListMixin):
    queryset = Product.objects
    search_fields = ['title', 'code']
    serializer_list = BOMProductMaterialListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            general_product_types_mapped__code='material',
            general_product_types_mapped__is_material=True
        ).select_related('sale_default_uom').prefetch_related()

    @swagger_auto_schema(
        operation_summary="BOM Product Material List",
        operation_description="Get BOM Product Material List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductToolsListForBOM(BaseListMixin):
    queryset = Product.objects
    search_fields = ['title', 'code']
    serializer_list = BOMProductMaterialListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            general_product_types_mapped__code='asset_tool',
            general_product_types_mapped__is_asset_tool=True
        ).select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="BOM Product Material List",
        operation_description="Get BOM Product Material List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# BEGIN
class BOMList(BaseListMixin, BaseCreateMixin):
    queryset = BOM.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'bom_type': ['exact']
    }
    serializer_list = BOMListSerializer
    serializer_create = BOMCreateSerializer
    serializer_detail = BOMDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('product')

    @swagger_auto_schema(
        operation_summary="BOM List",
        operation_description="Get BOM List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='bom', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create BOM",
        operation_description="Create new BOM",
        request_body=BOMCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='bom', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BOMDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = BOM.objects
    serializer_detail = BOMDetailSerializer
    serializer_update = BOMUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('product').prefetch_related(
            'bom_process_bom__labor__expense__uom',
            'bom_process_bom__labor__expense__price',
            'bom_process_bom__uom',
            'bom_summary_process_bom__labor',
            'bom_summary_process_bom__uom',
            'bom_material_component_bom__material',
            'bom_material_component_bom__uom',
            'bom_tool_bom__tool',
            'bom_tool_bom__uom'
        )

    @swagger_auto_schema(
        operation_summary="BOM detail",
        operation_description="Get BOM detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='bom', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update BOM",
        operation_description="Update BOM by ID",
        request_body=BOMUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='bom', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class BOMOrderList(BaseListMixin, BaseCreateMixin):
    queryset = BOM.objects
    search_fields = ['title', 'code']
    filterset_fields = {'product_id': ['exact']}
    serializer_list = BOMOrderListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="BOM List For Order",
        operation_description="Get BOM List For Order",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
