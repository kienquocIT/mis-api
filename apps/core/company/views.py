from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated


from apps.core.company.models import CompanyUserEmployee
from apps.core.company.mixins import CompanyDestroyMixin, CompanyListMixin
from apps.core.company.models import Company
from apps.shared import mask_view, BaseListMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.core.company.serializers import (
    CompanyCreateSerializer,
    CompanyListSerializer,
    CompanyDetailSerializer,
    CompanyUpdateSerializer,
    CompanyOverviewSerializer,
    CompanyUserNotMapEmployeeSerializer, CompanyOverviewDetailSerializer, CompanyOverviewConnectedSerializer,
)


class CompanyList(BaseListMixin, BaseCreateMixin):
    """
    Company List:
        GET: List
        POST: Create a new
    """
    queryset = Company.objects
    serializer_list = CompanyListSerializer
    serializer_create = CompanyCreateSerializer
    serializer_detail = CompanyDetailSerializer
    list_hidden_field = ['tenant_id']
    create_hidden_field = ['tenant_id']

    def get_queryset(self):
        return super().get_queryset().select_related('tenant')

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


class CompanyDetail(BaseRetrieveMixin, BaseUpdateMixin, CompanyDestroyMixin):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.select_related('tenant')
    serializer_detail = CompanyDetailSerializer

    @swagger_auto_schema(operation_summary='Detail Company')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Company", request_body=CompanyUpdateSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = CompanyUpdateSerializer
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete Company")
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CompanyListOverview(BaseListMixin):
    """
    Company Overview:
        GET: /company/list/overview
    """
    queryset = Company.objects
    serializer_list = CompanyOverviewSerializer
    list_hidden_field = ['tenant_id']

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list"
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CompanyUserNotMapEmployeeList(CompanyListMixin):
    queryset = CompanyUserEmployee.objects.select_related(
        'user'
    ).filter(
        employee=None
    )
    serializer_list = CompanyUserNotMapEmployeeSerializer

    @swagger_auto_schema(
        operation_summary="Company User Not Map Employee list",
        operation_description="Company User Not Map Employee list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list_company_user_employee(request, *args, **kwargs)


class CompanyOverviewDetail(BaseRetrieveMixin):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_detail = CompanyOverviewDetailSerializer

    @swagger_auto_schema(
        operation_summary='Detail Company Overview (0: All, 1: Employee Connected)'
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        if 'option' in kwargs:
            if kwargs['option'] == 1:
                self.serializer_detail = CompanyOverviewConnectedSerializer
        return self.retrieve(request, *args, **kwargs)
