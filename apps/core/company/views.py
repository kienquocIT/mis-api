from drf_yasg.utils import swagger_auto_schema
from apps.core.company.models import Company, CompanyUserEmployee
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, TypeCheck
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.shared import ResponseController
from apps.core.company.serializers import (
    CompanyCreateSerializer,
    CompanyListSerializer,
    CompanyDetailSerializer,
    CompanyUpdateSerializer,
    TenantInformationSerializer,
    CompanyOverviewSerializer, EmployeeListByCompanyOverviewSerializer, UserListByCompanyOverviewSerializer,
)


class CompanyList(BaseListMixin, BaseCreateMixin):
    """
    Company List:
        GET: List
        POST: Create a new
    """
    queryset = Company.object_normal
    serializer_list = CompanyListSerializer
    serializer_create = CompanyCreateSerializer
    serializer_detail = CompanyDetailSerializer
    list_hidden_field = ['tenant_id']
    create_hidden_field = ['tenant_id']

    def get_queryset(self):
        return super(CompanyList, self).get_queryset().select_related('tenant')

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


class CompanyListOverview(BaseListMixin):
    """
    Company Overview:
        GET: /company/list/overview
    """
    queryset = Company.object_normal
    serializer_list = CompanyOverviewSerializer
    list_hidden_field = ['tenant_id']

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserByCompanyOverviewDetail(APIView):
    @swagger_auto_schema(operation_summary='Get User List of Company ID for overview')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id', None)
        if company_id:
            try:
                company_obj = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                return ResponseController.notfound_404()
            if company_obj.tenant_id == request.user.tenant_current_id:
                maps = CompanyUserEmployee.object_normal.filter(company_id=company_id).select_related('user')
                objs = [x.user for x in maps if x.user is not None]
                ser = UserListByCompanyOverviewSerializer(objs, many=True)
                return ResponseController.success_200(data=ser.data, key_data='result')
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class EmployeeByCompanyOverviewDetail(BaseListMixin):
    queryset = CompanyUserEmployee.object_normal
    serializer_list = EmployeeListByCompanyOverviewSerializer
    ordering_fields = ['employee__first_name', 'employee__last_name']

    def get_queryset(self):
        return super(EmployeeByCompanyOverviewDetail, self).get_queryset().select_related('employee')

    @swagger_auto_schema(operation_summary='Get Employee List of Company ID for overview')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id', None)
        if company_id:
            try:
                company_obj = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                return ResponseController.notfound_404()
            if company_obj.tenant_id == request.user.tenant_current_id:
                return self.list(request, *args, **kwargs)
                # maps = CompanyUserEmployee.object_normal.filter(company_id=company_id).select_related('employee')
                # objs = [x.employee for x in maps if x.employee is not None]
                # ser = EmployeeListByCompanyOverviewSerializer(objs, many=True)
                # return ResponseController.success_200(data=ser.data, key_data='result')
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class CompanyLoginOfUserForOverviewDetail(APIView):
    @swagger_auto_schema(operation_summary='Get Company Login List of User for overview')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        user_id_list = request.data.get('user_id_list', '')
        company_id = kwargs.get('company_id', None)
        if user_id_list and company_id and TypeCheck.check_uuid(company_id):
            user_id_arr = []
            for item in list(set(user_id_list)):
                if TypeCheck.check_uuid(item):
                    user_id_arr.append(item)
                else:
                    return ResponseController.notfound_404()

            if user_id_arr:
                try:
                    company_obj = Company.objects.get(pk=company_id)
                except Company.DoesNotExist:
                    return ResponseController.notfound_404()

                company_id_list = Company.objects.filter(tenant_id=company_obj.tenant_id).values_list('id', flat=True)
                if company_id_list:
                    result = {}
                    for company_user_id in CompanyUserEmployee.object_normal.filter(
                            company_id__in=company_id_list, user_id__in=user_id_arr
                    ).values_list('company_id', 'user_id'):
                        com_id_0, user_id_1 = str(company_user_id[0]), str(company_user_id[1])
                        if user_id_1 in result:
                            result[user_id_1].append(com_id_0)
                        else:
                            result[user_id_1] = [com_id_0]
                    return ResponseController.success_200(data=result, key_data='result')
                return ResponseController.success_200({}, key_data='result')
        return ResponseController.notfound_404()
