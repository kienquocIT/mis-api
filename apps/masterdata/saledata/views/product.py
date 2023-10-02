from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import ProductPriceList
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from apps.masterdata.saledata.models.product import (
    ProductType, ProductCategory, ExpenseType, UnitOfMeasureGroup, UnitOfMeasure, Product,
)
from apps.masterdata.saledata.serializers.product import (
    ProductListSerializer, ProductCreateSerializer, ProductDetailSerializer, ProductUpdateSerializer,
    ProductForSaleListSerializer, UnitOfMeasureOfGroupLaborListSerializer
)
from apps.masterdata.saledata.serializers.product_masterdata import (
    ProductTypeListSerializer, ProductTypeCreateSerializer, ProductTypeDetailSerializer, ProductTypeUpdateSerializer,

    ProductCategoryListSerializer, ProductCategoryCreateSerializer,
    ProductCategoryDetailSerializer, ProductCategoryUpdateSerializer,

    ExpenseTypeListSerializer, ExpenseTypeCreateSerializer, ExpenseTypeDetailSerializer, ExpenseTypeUpdateSerializer,

    UnitOfMeasureGroupListSerializer, UnitOfMeasureGroupCreateSerializer,
    UnitOfMeasureGroupDetailSerializer, UnitOfMeasureUpdateSerializer,

    UnitOfMeasureListSerializer, UnitOfMeasureCreateSerializer,
    UnitOfMeasureGroupUpdateSerializer, UnitOfMeasureDetailSerializer
)


# Create your views here.
class ProductTypeList(BaseListMixin, BaseCreateMixin):
    queryset = ProductType.objects
    serializer_list = ProductTypeListSerializer
    serializer_create = ProductTypeCreateSerializer
    serializer_detail = ProductTypeDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

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


class ProductTypeDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProductType.objects
    serializer_list = ProductTypeListSerializer
    serializer_create = ProductTypeCreateSerializer
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


class ProductCategoryList(BaseListMixin, BaseCreateMixin):
    queryset = ProductCategory.objects
    serializer_list = ProductCategoryListSerializer
    serializer_create = ProductCategoryCreateSerializer
    serializer_detail = ProductCategoryDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

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


class ProductCategoryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ProductCategory.objects
    serializer_list = ProductCategoryListSerializer
    serializer_create = ProductCategoryCreateSerializer
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


class ExpenseTypeList(BaseListMixin, BaseCreateMixin):
    queryset = ExpenseType.objects
    serializer_list = ExpenseTypeListSerializer
    serializer_create = ExpenseTypeCreateSerializer
    serializer_detail = ExpenseTypeDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="ExpenseType list",
        operation_description="ExpenseType list",
    )
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ExpenseType",
        operation_description="Create new ExpenseType",
        request_body=ProductCategoryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExpenseTypeDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ExpenseType.objects
    serializer_list = ExpenseTypeListSerializer
    serializer_create = ExpenseTypeCreateSerializer
    serializer_detail = ExpenseTypeDetailSerializer
    serializer_update = ExpenseTypeUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail ExpenseType')
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary="Update ExpenseType", request_body=ExpenseTypeUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class UnitOfMeasureGroupList(BaseListMixin, BaseCreateMixin):
    queryset = UnitOfMeasureGroup.objects
    serializer_list = UnitOfMeasureGroupListSerializer
    serializer_create = UnitOfMeasureGroupCreateSerializer
    serializer_detail = UnitOfMeasureGroupDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related('unitofmeasure_group')

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


class UnitOfMeasureGroupDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = UnitOfMeasureGroup.objects
    serializer_list = UnitOfMeasureGroupListSerializer
    serializer_create = UnitOfMeasureGroupCreateSerializer
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
    }

    def get_queryset(self):
        return super().get_queryset().select_related('group')

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


class UnitOfMeasureDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = UnitOfMeasure.objects
    serializer_list = UnitOfMeasureListSerializer
    serializer_create = UnitOfMeasureCreateSerializer
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


class ProductList(BaseListMixin, BaseCreateMixin):
    queryset = Product.objects
    serializer_list = ProductListSerializer
    serializer_create = ProductCreateSerializer
    serializer_detail = ProductDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT
    search_fields = ['title']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'general_product_category',
            'general_uom_group',
            'sale_tax',
            'sale_default_uom',
            'inventory_uom'
        )

    @swagger_auto_schema(
        operation_summary="Product list",
        operation_description="Product list",
    )
    @mask_view(
        login_require=True, auth_require=False,
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


class ProductDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Product.objects
    serializer_list = ProductListSerializer
    serializer_create = ProductCreateSerializer
    serializer_detail = ProductDetailSerializer
    serializer_update = ProductUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'product_price_product__currency_using',
            'product_price_product__price_list',
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
        login_require=True, auth_require=False,
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


# Products use for sale applications
class ProductForSaleList(BaseListMixin):
    queryset = Product.objects
    search_fields = ['title']
    serializer_list = ProductForSaleListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'general_product_category',
            'general_uom_group',
            "sale_default_uom",
            "sale_tax",
            "sale_currency_using",
        ).prefetch_related(
            'general_product_types_mapped',
            Prefetch(
                'product_price_product',
                queryset=ProductPriceList.objects.select_related('price_list'),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Product for sale list",
        operation_description="Product for sale list",
    )
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UnitOfMeasureOfGroupLaborList(BaseListMixin):
    queryset = UnitOfMeasure.objects
    serializer_list = UnitOfMeasureOfGroupLaborListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'group',
        ).filter(group__is_default=1)

    @swagger_auto_schema(
        operation_summary="Product for sale list",
        operation_description="Product for sale list",
    )
    @mask_view(login_require=True, auth_require=False, )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
