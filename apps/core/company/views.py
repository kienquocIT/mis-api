from drf_yasg.utils import swagger_auto_schema

from apps.core.company.models import Company
from apps.core.company.serializers import CompanyCreateSerializer, CompanyListSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin


class CompanyList(BaseListMixin, BaseCreateMixin):
    """
    Company List:
        GET: List
        POST: Create a new
    """
    queryset = Company.object_normal.all()
    serializer_list = CompanyListSerializer
    serializer_create = CompanyCreateSerializer
    serializer_detail = CompanyListSerializer
    list_hidden_field = ['tenant_id']
    create_hidden_field = ['tenant_id']

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Company",
        operation_description="Create new Company",
        request_body=CompanyCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
