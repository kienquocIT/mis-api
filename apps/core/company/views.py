from drf_yasg.utils import swagger_auto_schema
from apps.core.company.models import Company
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.shared import ResponseController
from apps.core.company.serializers import (CompanyCreateSerializer,
                                           CompanyListSerializer,
                                           CompanyDetailSerializer,
                                           CompanyUpdateSerializer,
                                           TenantInformationSerializer)


class CompanyList(BaseListMixin, BaseCreateMixin):
    """
    Company List:
        GET: List
        POST: Create a new
    """
    queryset = Company.object_normal.select_related('tenant')
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


class CompanyDetail(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary='Detail Company')
    def get(self, request, pk, *args, **kwargs):
        if request.user:
            company = Company.objects.get(pk=pk)
            company_ser = CompanyDetailSerializer(company)
            return ResponseController.success_200(data=company_ser.data, key_data='result')
        return ResponseController.unauthorized_401()

    @swagger_auto_schema(operation_summary="Update User", request_body=CompanyUpdateSerializer)
    def put(self, request, pk, *args, **kwargs):
        if request.user:
            company = Company.objects.get(pk=pk)
            company_ser = CompanyUpdateSerializer(instance=company, data=request.data)
            if company_ser.is_valid():
                company_ser.save()
                return ResponseController.success_200(
                    data=company_ser.data,
                    key_data='result',
                )
            return ResponseController.bad_request_400(msg='Setup new user was raised undefined error.')
        return ResponseController.unauthorized_401()

    @swagger_auto_schema(operation_summary="Delete Company")
    def delete(self, request, pk, *args, **kwargs):
        if request.user:
            company = Company.objects.get(pk=pk)
            company.delete()
            return ResponseController.success_200(data={'state': 'Delete successfully'}, key_data='result')
        return ResponseController.unauthorized_401()


class CompanyOverviewList(BaseListMixin, BaseCreateMixin):
    queryset = Company.object_normal.all()
    serializer_list = TenantInformationSerializer

    def get_queryset(self):
        return Company.object_normal.filter(tenant_id=self.request.user.tenant_current_id)
    @swagger_auto_schema(
        operation_summary="Tenant Information",
        operation_description="Tenant Information",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)