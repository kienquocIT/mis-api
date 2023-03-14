from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from apps.sale.saledata.models.product import (
    ProductType
)
from apps.sale.saledata.serializers.product import (
    ProductTypeListSerializer, ProductTypeCreateSerializer, ProductTypeDetailSerializer
)


# Create your views here.
class ProductTypeList(BaseListMixin, BaseCreateMixin):
    queryset = ProductType.objects
    serializer_list = ProductTypeListSerializer
    serializer_create = ProductTypeCreateSerializer
    serializer_detail = ProductTypeDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="ProductType list",
        operation_description="ProductType list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().filter(tenant=request.user.tenant_current_id)
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ProductType",
        operation_description="Create new ProductType",
        request_body=ProductTypeCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
