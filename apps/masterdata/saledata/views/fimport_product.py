from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Product, Manufacturer
from apps.masterdata.saledata.serializers.fimport_product import (
    ProductImportCreateSerializer, ProductImportDetailSerializer,
    ProductManufacturerImportDetailSerializer, ProductManufacturerImportCreateSerializer
)
from apps.shared import BaseCreateMixin, mask_view


class ProductImportList(BaseCreateMixin):
    queryset = Product.objects
    serializer_create = ProductImportCreateSerializer
    serializer_detail = ProductImportDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Product",
        request_body=ProductImportCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductManufacturerImportList(BaseCreateMixin):
    queryset = Manufacturer.objects
    serializer_create = ProductManufacturerImportCreateSerializer
    serializer_detail = ProductManufacturerImportDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Product Manufacturer",
        request_body=ProductManufacturerImportCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
