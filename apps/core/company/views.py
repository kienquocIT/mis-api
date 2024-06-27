from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from apps.core.company.models import CompanyUserEmployee, CompanyConfig
from apps.core.company.mixins import CompanyDestroyMixin
from apps.core.company.models import Company
from apps.shared import (
    mask_view, BaseListMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin, ResponseController,
    HttpMsg,
)
from apps.core.company.serializers import (
    CompanyCreateSerializer,
    CompanyListSerializer,
    CompanyDetailSerializer,
    CompanyUpdateSerializer,
    CompanyOverviewSerializer,
    CompanyUserNotMapEmployeeSerializer, CompanyOverviewDetailSerializer, CompanyOverviewConnectedSerializer,
    CompanyConfigDetailSerializer, CompanyConfigUpdateSerializer, RestoreDefaultOpportunityConfigStageSerializer,
    CompanyUploadLogoSerializer,
)


class CompanyConfigDetail(APIView):
    serializer_class = CompanyConfigDetailSerializer

    @swagger_auto_schema(
        operation_summary='Get config of Company',
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        try:
            company_id = self.request.query_params['company_id'] \
                if 'company_id' in self.request.query_params else request.user.company_current_id
            obj = CompanyConfig.objects.select_related('currency').get(
                company_id=company_id,
                **{'force_cache': True}
            )
            return ResponseController.success_200(data=CompanyConfigDetailSerializer(obj).data, key_data='result')
        except CompanyConfig.DoesNotExist:
            pass
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Update config of Company',
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True,
        label_code='company', model_code='company', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        try:
            company_id = self.request.query_params['company_id'] \
                if 'company_id' in self.request.query_params else request.user.company_current_id
            obj = CompanyConfig.objects.select_related('currency').get(
                company_id=company_id
            )
            ser = CompanyConfigUpdateSerializer(obj, data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save()
            return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
        except CompanyConfig.DoesNotExist:
            pass
        return ResponseController.notfound_404()


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
    search_fields = ('title', 'code')
    filterset_fields = ('title', 'code')

    def get_queryset(self):
        return super().get_queryset().select_related('tenant')

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Company",
        operation_description="Create new Company",
        request_body=CompanyCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True,
        label_code='company', model_code='company', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CompanyDetail(BaseRetrieveMixin, BaseUpdateMixin, CompanyDestroyMixin):
    queryset = Company.objects
    serializer_detail = CompanyDetailSerializer
    serializer_update = CompanyUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('tenant')

    @swagger_auto_schema(operation_summary='Detail Company')
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True,
        label_code='company', model_code='company', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Company", request_body=CompanyUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True,
        label_code='company', model_code='company', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete Company")
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True,
        label_code='company', model_code='company', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CompanyUploadLogo(BaseUpdateMixin):
    parser_classes = [MultiPartParser]
    queryset = Company.objects
    serializer_update = CompanyUploadLogoSerializer

    def get_object(self):
        instance = super().get_object()
        if instance and self.request.user.company_current == instance:
            return instance
        raise Company.DoesNotExist

    def write_log(self, *args, **kwargs):
        kwargs['request_data'] = {}
        super().write_log(*args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Company", request_body=CompanyUploadLogoSerializer)
    @mask_view(
        login_require=True, auth_require=False, allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CompanyListOverview(BaseListMixin):
    """
    Company Overview:
        GET: /company/list/overview
    """
    queryset = Company.objects
    serializer_list = CompanyOverviewSerializer
    list_hidden_field = ['tenant_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('hr_employee_belong_to_company')

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list"
    )
    @mask_view(login_require=True, auth_require=True, allow_admin_tenant=True, allow_admin_company=True,)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CompanyUserNotMapEmployeeList(BaseListMixin):
    queryset = CompanyUserEmployee.objects
    serializer_list = CompanyUserNotMapEmployeeSerializer
    list_hidden_field = ['company']
    search_fields = ('user__first_name', 'employee__first_name', 'user__last_name', 'employee__last_name', )
    ordering = ['-employee']

    def get_queryset(self):
        return super().get_queryset().select_related('user').filter(user__isnull=False, employee__isnull=True)

    def get_filter_auth(self) -> dict:
        return {}

    @swagger_auto_schema(
        operation_summary="Company User Not Map Employee list",
        operation_description="Company User Not Map Employee list",
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='view',
        use_custom_get_filter_auth=True,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CompanyOverviewDetail(BaseRetrieveMixin):
    queryset = Company.objects.all()
    serializer_detail = CompanyOverviewDetailSerializer

    @swagger_auto_schema(
        operation_summary='Detail Company Overview (0: All, 1: Employee Connected)'
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_tenant=True, allow_admin_company=True,
        label_code='company', model_code='company', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        if 'option' in kwargs:
            if kwargs['option'] == 1:
                self.serializer_detail = CompanyOverviewConnectedSerializer
        return self.retrieve(request, *args, **kwargs)


class RestoreDefaultOpportunityConfigStage(BaseUpdateMixin):
    queryset = Company.objects
    serializer_update = RestoreDefaultOpportunityConfigStageSerializer

    @swagger_auto_schema(
        operation_summary='Restore Default Opportunity Config Stage'
    )
    @mask_view(login_require=True, auth_require=True, allow_admin_tenant=True, allow_admin_company=True)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
