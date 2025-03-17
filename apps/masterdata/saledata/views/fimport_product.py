from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import Product
from apps.masterdata.saledata.serializers.fimport_product import (
    ProductImportListSerializer, ProductImportDetailSerializer
)
from apps.shared import BaseCreateMixin, mask_view

class ProductImportList(BaseCreateMixin):
    queryset = Product.objects
    serializer_create = ProductImportListSerializer
    serializer_detail = ProductImportDetailSerializer
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Import Product",
        request_body=ProductImportListSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
