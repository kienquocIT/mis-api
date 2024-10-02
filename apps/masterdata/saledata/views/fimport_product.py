from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import (
    Contact, Salutation, Currency, AccountGroup, AccountType, Industry,
    PaymentTerm, Account, UnitOfMeasureGroup, ProductType, TaxCategory, UnitOfMeasure, Tax, Product,
)
from apps.masterdata.saledata.serializers.fimport_product import ProductImportSerializer, ProductImportReturnSerializer
from apps.shared import BaseCreateMixin, mask_view

from apps.masterdata.saledata.serializers.fimport import (
    SaleDataContactImportReturnSerializer,
    SaleDataContactImportSerializer, SalutationImportSerializer, SalutationImportReturnSerializer,
    SaleDataCurrencyImportSerializer, SaleDataCurrencyImportReturnSerializer, AccountGroupImportSerializer,
    AccountGroupImportReturnSerializer, AccountTypeImportSerializer, AccountTypeImportReturnSerializer,
    IndustryImportSerializer, IndustryImportReturnSerializer, PaymentTermImportSerializer,
    PaymentTermImportReturnSerializer, SaleDataAccountImportSerializer, SaleDataAccountImportReturnSerializer,
    ProductUOMGroupImportSerializer, ProductUOMGroupImportReturnSerializer, ProductProductTypeImportSerializer,
    ProductProductTypeImportReturnSerializer, ProductProductCategoryImportSerializer,
    ProductProductCategoryImportReturnSerializer, PriceTaxCategoryImportSerializer,
    PriceTaxCategoryImportReturnSerializer, ProductUOMImportSerializer, ProductUOMImportReturnSerializer,
    PriceTaxImportSerializer, PriceTaxImportReturnSerializer,
)

class ProductImport(BaseCreateMixin):
    queryset = Product.objects
    serializer_create = ProductImportSerializer
    serializer_detail = ProductImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Product",
        request_body=ProductImportSerializer,
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)