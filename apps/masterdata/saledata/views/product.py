from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import ProductPriceList
from apps.masterdata.saledata.serializers.product_import_db import (
    ProductQuotationCreateSerializerLoadDB, ProductQuotationDetailSerializerLoadDB
)
from apps.sales.production.models import BOM
from apps.sales.saleorder.models import SaleOrderProduct
from apps.shared import (
    mask_view, ResponseController,
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
)
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure, Product, Manufacturer,
)
from apps.masterdata.saledata.serializers.product import (
    ProductListSerializer, ProductCreateSerializer,
    ProductDetailSerializer, ProductUpdateSerializer,
    UnitOfMeasureOfGroupLaborListSerializer, ProductQuickCreateSerializer,
)
from apps.masterdata.saledata.serializers.product_masterdata import (
    ProductTypeListSerializer, ProductTypeCreateSerializer,
    ProductTypeDetailSerializer, ProductTypeUpdateSerializer,
    ProductCategoryListSerializer, ProductCategoryCreateSerializer,
    ProductCategoryDetailSerializer, ProductCategoryUpdateSerializer,
    UnitOfMeasureGroupListSerializer, UnitOfMeasureGroupCreateSerializer,
    UnitOfMeasureGroupDetailSerializer, UnitOfMeasureUpdateSerializer,
    UnitOfMeasureListSerializer, UnitOfMeasureCreateSerializer,
    UnitOfMeasureGroupUpdateSerializer, UnitOfMeasureDetailSerializer, ManufacturerListSerializer,
    ManufacturerCreateSerializer, ManufacturerDetailSerializer, ManufacturerUpdateSerializer
)
from apps.masterdata.saledata.serializers.product_custom import (
    ProductForSaleListSerializer, ProductForSaleDetailSerializer
)


# Create your views here.
class ProductTypeList(BaseListMixin, BaseCreateMixin):
    queryset = ProductType.objects
    search_fields = ['title']
    filterset_fields = {
        'is_default': ['exact'],
    }
    serializer_list = ProductTypeListSerializer
    serializer_create = ProductTypeCreateSerializer
    serializer_detail = ProductTypeDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="ProductType list",
        operation_description="ProductType list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ProductType",
        operation_description="Create new ProductType",
        request_body=ProductTypeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductTypeDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProductType.objects
    serializer_detail = ProductTypeDetailSerializer
    serializer_update = ProductTypeUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail ProductType')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update ProductType", request_body=ProductTypeUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Remove ProductType'
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.has_related_records(instance):
            return ResponseController.bad_request_400(msg="This ProductType is referenced by some records.")
        if instance.is_default:
            return ResponseController.bad_request_400(msg="This ProductType is system default.")
        instance.is_delete = True
        instance.save(update_fields=['is_delete'])
        return ResponseController.success_200({}, key_data='result')


class ProductCategoryList(BaseListMixin, BaseCreateMixin):
    queryset = ProductCategory.objects
    search_fields = ['title']
    serializer_list = ProductCategoryListSerializer
    serializer_create = ProductCategoryCreateSerializer
    serializer_detail = ProductCategoryDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="ProductCategory list",
        operation_description="ProductCategory list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ProductCategory",
        operation_description="Create new ProductCategory",
        request_body=ProductCategoryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductCategoryDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProductCategory.objects
    serializer_detail = ProductCategoryDetailSerializer
    serializer_update = ProductCategoryUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail ProductCategory')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update ProductCategory", request_body=ProductCategoryUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Remove ProductCategory'
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UnitOfMeasureGroupList(BaseListMixin, BaseCreateMixin):
    queryset = UnitOfMeasureGroup.objects
    search_fields = ['title']
    serializer_list = UnitOfMeasureGroupListSerializer
    serializer_create = UnitOfMeasureGroupCreateSerializer
    serializer_detail = UnitOfMeasureGroupDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            is_delete=False
        ).prefetch_related('unitofmeasure_group').order_by('-is_default', 'code')

    @swagger_auto_schema(
        operation_summary="UnitOfMeasureGroup list",
        operation_description="UnitOfMeasureGroup list",
    )
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create UnitOfMeasureGroup",
        operation_description="Create new UnitOfMeasureGroup",
        request_body=UnitOfMeasureGroupCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UnitOfMeasureGroupDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = UnitOfMeasureGroup.objects
    serializer_detail = UnitOfMeasureGroupDetailSerializer
    serializer_update = UnitOfMeasureGroupUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail UnitOfMeasureGroup')
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update UnitOfMeasureGroup", request_body=UnitOfMeasureGroupUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Remove UnitOfMeasureGroup'
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.has_related_records(instance):
            return ResponseController.bad_request_400(msg="This UnitOfMeasureGroup is referenced by some records.")
        if instance.is_default:
            return ResponseController.bad_request_400(msg="This UnitOfMeasureGroup is system default.")
        instance.is_delete = True
        instance.save(update_fields=['is_delete'])
        return ResponseController.success_200({}, key_data='result')


class UnitOfMeasureList(BaseListMixin, BaseCreateMixin):
    queryset = UnitOfMeasure.objects
    search_fields = ['title']
    serializer_list = UnitOfMeasureListSerializer
    serializer_create = UnitOfMeasureCreateSerializer
    serializer_detail = UnitOfMeasureDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_fields = {
        'group': ['exact', 'in'],
        'group_id': ['exact', 'in'],
        'group__code': ['exact'],
    }

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False).select_related('group')

    @swagger_auto_schema(
        operation_summary="UnitOfMeasure list",
        operation_description="UnitOfMeasure list",
    )
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create UnitOfMeasure",
        operation_description="Create new UnitOfMeasure",
        request_body=UnitOfMeasureCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UnitOfMeasureDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = UnitOfMeasure.objects
    serializer_detail = UnitOfMeasureDetailSerializer
    serializer_update = UnitOfMeasureUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('group')

    @swagger_auto_schema(operation_summary='Detail UnitOfMeasure')
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update UnitOfMeasure", request_body=UnitOfMeasureUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Remove UnitOfMeasure'
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.has_related_records(instance):
            return ResponseController.bad_request_400(msg="This UnitOfMeasure is referenced by some records.")
        if instance.is_default:
            return ResponseController.bad_request_400(msg="This UnitOfMeasure is system default.")
        instance.is_delete = True
        instance.save(update_fields=['is_delete'])
        return ResponseController.success_200({}, key_data='result')


class ManufacturerList(BaseListMixin, BaseCreateMixin):
    queryset = Manufacturer.objects
    search_fields = ['title']
    serializer_list = ManufacturerListSerializer
    serializer_create = ManufacturerCreateSerializer
    serializer_detail = ManufacturerDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="Manufacturer list",
        operation_description="Manufacturer list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Manufacturer",
        operation_description="Create new Manufacturer",
        request_body=ManufacturerCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ManufacturerDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = Manufacturer.objects
    serializer_detail = ManufacturerDetailSerializer
    serializer_update = ManufacturerUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Manufacturer')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update Manufacturer", request_body=ManufacturerUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Remove Manufacturer'
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProductList(BaseListMixin, BaseCreateMixin):
    queryset = Product.objects
    serializer_list = ProductListSerializer
    serializer_create = ProductCreateSerializer
    serializer_detail = ProductDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    search_fields = [
        'code',
        'title',
    ]
    filterset_fields = {
        "general_product_types_mapped__id": ['exact']
    }

    def get_queryset(self):
        main_queryset = super().get_queryset().select_related(
            'general_product_category',
            'general_uom_group',
            'sale_tax',
            'sale_default_uom',
            'inventory_uom'
        ).prefetch_related(
            'general_product_types_mapped',
            Prefetch(
                'product_price_product',
                queryset=ProductPriceList.objects.select_related('price_list')
            )
        )
        return self.get_queryset_custom_direct_page(main_queryset)

    @swagger_auto_schema(
        operation_summary="Product list",
        operation_description="Product list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Product",
        operation_description="Create new Product",
        request_body=ProductCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductQuickCreateList(BaseListMixin, BaseCreateMixin):
    queryset = Product.objects
    serializer_create = ProductQuickCreateSerializer
    serializer_detail = ProductListSerializer
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'general_product_category',
            'general_uom_group',
            'sale_tax',
            'sale_default_uom',
            'inventory_uom',
        ).prefetch_related(
            'general_product_types_mapped',
            Prefetch(
                'product_price_product',
                queryset=ProductPriceList.objects.select_related('price_list'),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Quick Create Product",
        operation_description="Quick Create new Product",
        request_body=ProductQuickCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Product.objects
    serializer_detail = ProductDetailSerializer
    serializer_update = ProductUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'product_price_product__currency_using',
            'product_price_product__price_list',
            'product_variant_attributes',
            'product_variants',
            'product_warehouse_product',
        ).select_related(
            'general_product_category',
            'general_uom_group',
            'sale_default_uom',
            'sale_tax',
            'sale_currency_using',
            'inventory_uom',
            'purchase_default_uom',
            'purchase_tax'
        )

    @swagger_auto_schema(operation_summary='Detail Product')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update Product", request_body=ProductUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


# Products use for sale/ purchase/ inventory
class ProductForSaleList(BaseListMixin):
    queryset = Product.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'id': ['exact', 'in'],
        'general_product_types_mapped__is_goods': ['exact'],
        'general_product_types_mapped__is_finished_goods': ['exact'],
        'general_product_types_mapped__is_material': ['exact'],
        'general_product_types_mapped__is_tool': ['exact'],
        'general_product_types_mapped__is_service': ['exact'],
        'bom_product__opportunity_id': ['exact', 'isnull'],
        'bom_product': ['isnull'],
    }
    serializer_list = ProductForSaleListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'general_product_category',
            'general_uom_group',
            "sale_default_uom",
            "sale_tax",
            "sale_currency_using",
            "purchase_default_uom",
            "purchase_tax",
            "inventory_uom",
        ).prefetch_related(
            'general_product_types_mapped',
            Prefetch(
                'product_price_product',
                queryset=ProductPriceList.objects.select_related('price_list', 'uom_using'),
            ),
            Prefetch(
                'bom_product',
                queryset=BOM.objects.filter(
                    opportunity__isnull=True,
                    system_status=3,
                ),
                to_attr='filtered_bom'
            ),
            Prefetch(
                'bom_product',
                queryset=BOM.objects.filter(
                    opportunity__isnull=False,
                    system_status=3,
                ),
                to_attr='filtered_bom_opp'
            ),
            Prefetch(
                'sale_order_product_product',
                queryset=SaleOrderProduct.objects.filter(
                    sale_order__system_status__in=[0, 1],
                    sale_order__opportunity__isnull=False
                ),
                to_attr='filtered_so_product_using'
            ),
            Prefetch(
                'sale_order_product_product',
                queryset=SaleOrderProduct.objects.filter(
                    sale_order__system_status__in=[2, 3],
                    sale_order__opportunity__isnull=False
                ),
                to_attr='filtered_so_product_finished'
            ),
        )

    @swagger_auto_schema(
        operation_summary="Product Sale list",
        operation_description="Product Sale list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductForSaleDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Product.objects
    serializer_detail = ProductForSaleDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Product Sale Detail",
        operation_description="Get Product Sale Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UnitOfMeasureOfGroupLaborList(BaseListMixin):
    queryset = UnitOfMeasure.objects
    search_fields = ['title']
    serializer_list = UnitOfMeasureOfGroupLaborListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False).select_related(
            'group',
        ).filter(group__is_default=1)

    @swagger_auto_schema(
        operation_summary="Product for sale list",
        operation_description="Product for sale list",
    )
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductQuotationListLoadDB(BaseCreateMixin):
    queryset = Product.objects
    serializer_create = ProductQuotationCreateSerializerLoadDB
    serializer_detail = ProductQuotationDetailSerializerLoadDB
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Product Quotation Create ImportDB",
        operation_description="Product Quotation Create ImportDB",
        request_body=ProductQuotationCreateSerializerLoadDB,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saledata', model_code='product', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_current': request.user.tenant_current,
            'company_current': request.user.company_current,
            'employee_current': request.user.employee_current
        }
        return self.create(request, *args, **kwargs)
