from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import (
    Contact, Salutation, Currency, AccountGroup, AccountType, Industry,
    PaymentTerm, Account, UnitOfMeasureGroup, ProductType,
)
from apps.masterdata.saledata.serializers import ProductTypeCreateSerializer
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
    ProductProductCategoryImportReturnSerializer,
)


class CurrencyImport(BaseCreateMixin):
    queryset = Currency.objects
    serializer_create = SaleDataCurrencyImportSerializer
    serializer_detail = SaleDataCurrencyImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import currency",
        request_body=SaleDataCurrencyImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountGroupImport(BaseCreateMixin):
    queryset = AccountGroup.objects
    serializer_create = AccountGroupImportSerializer
    serializer_detail = AccountGroupImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Account Group",
        request_body=AccountGroupImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountTypeImport(BaseCreateMixin):
    queryset = AccountType.objects
    serializer_create = AccountTypeImportSerializer
    serializer_detail = AccountTypeImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import AccountType",
        request_body=AccountTypeImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class IndustryImport(BaseCreateMixin):
    queryset = Industry.objects
    serializer_create = IndustryImportSerializer
    serializer_detail = IndustryImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Industry",
        request_body=IndustryImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentTermImport(BaseCreateMixin):
    queryset = PaymentTerm.objects
    serializer_create = PaymentTermImportSerializer
    serializer_detail = PaymentTermImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Payment terms",
        request_body=PaymentTermImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SalutationImport(BaseCreateMixin):
    queryset = Salutation.objects
    serializer_create = SalutationImportSerializer
    serializer_detail = SalutationImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Salutation",
        request_body=SalutationImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ContactImport(BaseCreateMixin):
    queryset = Contact.objects
    serializer_create = SaleDataContactImportSerializer
    serializer_detail = SaleDataContactImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_inherit_id']

    @swagger_auto_schema(
        operation_summary="Import Contact",
        request_body=SaleDataContactImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        employee_require=True,
        label_code='saledata', model_code='contact', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AccountImport(BaseCreateMixin):
    queryset = Account.objects
    serializer_create = SaleDataAccountImportSerializer
    serializer_detail = SaleDataAccountImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_inherit_id']

    @swagger_auto_schema(
        operation_summary="Import Account",
        request_body=SaleDataAccountImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        employee_require=True,
        label_code='saledata', model_code='account', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductUOMGroupImport(BaseCreateMixin):
    queryset = UnitOfMeasureGroup.objects
    serializer_create = ProductUOMGroupImportSerializer
    serializer_detail = ProductUOMGroupImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Product UOM Group",
        request_body=AccountGroupImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ProductProductTypeImport(BaseCreateMixin):
    queryset = ProductType.objects
    serializer_create = ProductProductTypeImportSerializer
    serializer_detail = ProductProductTypeImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Product Type",
        request_body=ProductProductTypeImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ProductProductCategoryImport(BaseCreateMixin):
    queryset = ProductType.objects
    serializer_create = ProductProductCategoryImportSerializer
    serializer_detail = ProductProductCategoryImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Product Category",
        request_body=ProductProductCategoryImportSerializer
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        allow_admin_tenant=True,
        allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
