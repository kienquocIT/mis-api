from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.assettools.models import AssetToolsConfig
from apps.masterdata.saledata.models import Product, ProductType, Expense
from apps.sales.production.models import BOM
from apps.sales.production.serializers.bom import BOMProductMaterialListSerializer, LaborListForBOMSerializer, \
    BOMUpdateSerializer, BOMDetailSerializer, BOMCreateSerializer, BOMListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


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
        material_type = ProductType.objects.filter(
            title='Nguyên vật liệu',
            company=self.request.user.company_current,
            tenant=self.request.user.tenant_current
        ).first()
        if material_type:
            return super().get_queryset().filter(
                general_product_types_mapped__in=[material_type.id]
            ).select_related(
                'sale_default_uom'
            ).prefetch_related(
                'product_price_product__uom_using', 'product_price_product__price_list'
            )
        return super().get_queryset().none()

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
        tool_config_type = AssetToolsConfig.objects.filter(
            employee_tools_list_access__in=[self.request.user.employee_current_id],
            company=self.request.user.company_current,
        ).first()
        if tool_config_type:
            tool_type = tool_config_type.product_type
            return super().get_queryset().filter(
                general_product_types_mapped__in=[tool_type.id]
            ).select_related().prefetch_related()
        return super().get_queryset().none()

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
    filterset_fields = {}
    serializer_list = BOMListSerializer
    serializer_create = BOMCreateSerializer
    serializer_detail = BOMDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related()

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
        return super().get_queryset().select_related().prefetch_related()

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
