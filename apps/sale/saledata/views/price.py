from drf_yasg.utils import swagger_auto_schema
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

from apps.sale.saledata.models.price import (
    TaxCategory, Tax, Currency, Price
)
from apps.sale.saledata.serializers.price import (
    TaxCategoryListSerializer, TaxCategoryCreateSerializer, TaxCategoryDetailSerializer, TaxCategoryUpdateSerializer,
    TaxListSerializer, TaxCreateSerializer, TaxDetailSerializer, TaxUpdateSerializer,
    CurrencyListSerializer, CurrencyCreateSerializer, CurrencyDetailSerializer, CurrencyUpdateSerializer,
    CurrencySyncWithVCBSerializer,
    PriceListSerializer, PriceCreateSerializer, PriceDetailSerializer, PriceUpdateSerializer,
    PriceListUpdateProductsSerializer, PriceListDeleteProductsSerializer, ProductCreateInPriceListSerializer,
    DeleteCurrencyFromPriceListSerializer
)


# Create your views here.
class TaxCategoryList(BaseListMixin, BaseCreateMixin):
    queryset = TaxCategory.objects
    serializer_list = TaxCategoryListSerializer
    serializer_create = TaxCategoryCreateSerializer
    serializer_detail = TaxCategoryDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="TaxCategory list",
        operation_description="TaxCategory list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create TaxCategory",
        operation_description="Create new TaxCategory",
        request_body=TaxCategoryCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TaxCategoryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = TaxCategory.objects
    serializer_list = TaxCategoryListSerializer
    serializer_detail = TaxCategoryDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail TaxCategory')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update TaxCategory", request_body=TaxCategoryUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = TaxCategoryUpdateSerializer
        return self.update(request, *args, **kwargs)


class TaxList(BaseListMixin, BaseCreateMixin):
    queryset = Tax.objects.select_related('category')
    serializer_list = TaxListSerializer
    serializer_create = TaxCreateSerializer
    serializer_detail = TaxDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Tax list",
        operation_description="Tax list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Tax",
        operation_description="Create new Tax",
        request_body=TaxCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TaxDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Tax.objects.select_related('category')
    serializer_list = TaxListSerializer
    serializer_detail = TaxDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Tax')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Tax", request_body=TaxUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = TaxUpdateSerializer
        return self.update(request, *args, **kwargs)


class CurrencyList(BaseListMixin, BaseCreateMixin):
    queryset = Currency.objects
    serializer_list = CurrencyListSerializer
    serializer_create = CurrencyCreateSerializer
    serializer_detail = CurrencyDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Currency list",
        operation_description="Currency list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Currency",
        operation_description="Create new Currency",
        request_body=CurrencyCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CurrencyDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Currency.objects
    serializer_list = CurrencyListSerializer
    serializer_detail = CurrencyDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Currency')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Currency", request_body=CurrencyUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = CurrencyUpdateSerializer
        return self.update(request, *args, **kwargs)


class SyncWithVCB(BaseUpdateMixin):
    queryset = Currency.objects
    serializer_list = CurrencyListSerializer
    serializer_detail = CurrencySyncWithVCBSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary="Sync With VCB Currency", request_body=CurrencySyncWithVCBSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = CurrencySyncWithVCBSerializer
        return self.update(request, *args, **kwargs)


class PriceList(BaseListMixin, BaseCreateMixin):
    queryset = Price.objects
    serializer_list = PriceListSerializer
    serializer_create = PriceCreateSerializer
    serializer_detail = PriceDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Price list",
        operation_description="Price list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Price",
        operation_description="Create new Price",
        request_body=PriceCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PriceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Price.objects
    serializer_list = PriceListSerializer
    serializer_detail = PriceDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Price ')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Price List Setting", request_body=PriceUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = PriceUpdateSerializer
        return self.update(request, *args, **kwargs)


class UpdateProductsForPriceList(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Price.objects  # noqa
    serializer_list = PriceListSerializer
    serializer_detail = PriceDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Price List')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Price List's Products",
        request_body=PriceListUpdateProductsSerializer
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = PriceListUpdateProductsSerializer
        return self.update(request, *args, **kwargs)


class DeleteProductsForPriceList(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Price.objects  # noqa
    serializer_list = PriceListSerializer
    serializer_detail = PriceDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary='Detail Price List')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Price List's Products",
        request_body=PriceListDeleteProductsSerializer
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = PriceListDeleteProductsSerializer
        return self.update(request, *args, **kwargs)


class ProductAddFromPriceList(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Price.objects
    serializer_list = PriceListSerializer
    serializer_detail = PriceDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Create Product from Price List",
        operation_description="Create new Product from Price List",
        request_body=ProductCreateInPriceListSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = ProductCreateInPriceListSerializer
        return self.update(request, *args, **kwargs)


class DeleteCurrencyFromPriceList(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Price.objects # noqa
    serializer_list = PriceListSerializer
    serializer_detail = PriceDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Delete Currency from Price List",
        operation_description="Delete Currency from Price List",
        request_body=DeleteCurrencyFromPriceListSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = DeleteCurrencyFromPriceListSerializer
        return self.update(request, *args, **kwargs)
