from datetime import timedelta

from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, serializers
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from apps.core.hr.models import Employee
from apps.core.hr.serializers.employee_serializers import (
    EmployeeListSerializer, EmployeeCreateSerializer,
    EmployeeDetailSerializer, EmployeeUpdateSerializer,
    EmployeeListByOverviewTenantSerializer, EmployeeListMinimalByOverviewTenantSerializer,
    EmployeeUploadAvatarSerializer,
)
from apps.shared import (
    BaseUpdateMixin, mask_view, BaseRetrieveMixin, BaseListMixin, BaseCreateMixin, HRMsg,
    ResponseController, HttpMsg,
)
from apps.shared.media_cloud_apis import APIUtil, MediaForceAPI


class EmployeeUploadAvatar(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(request_body=EmployeeUploadAvatarSerializer)
    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, **kwargs):
        employee_obj = request.user.employee_current
        if employee_obj:
            ser = EmployeeUploadAvatarSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            uploaded_file = request.FILES.get('file')
            resp = MediaForceAPI.call_upload_avatar(employee_obj=employee_obj, f_img=uploaded_file)
            if resp.state:
                employee_obj.media_avatar_hash = resp.result['media_path_hash']
                employee_obj.save(update_fields=['media_avatar_hash'])
                return ResponseController.success_200(
                    data={'detail': HttpMsg.SUCCESSFULLY, 'media_path_hash': resp.result['media_path_hash']}
                )
            return ResponseController.bad_request_400(msg=resp.errors)
        return ResponseController.forbidden_403()


class EmployeeList(BaseListMixin, BaseCreateMixin):
    queryset = Employee.objects
    search_fields = ["search_content"]
    filterset_fields = {
        "role__id": ["exact", "in"]
    }

    serializer_list = EmployeeListSerializer
    serializer_detail = EmployeeListSerializer
    serializer_create = EmployeeCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'group',
        ).prefetch_related('role')

    def error_auth_require(self):
        return self.list_empty()

    @swagger_auto_schema(
        operation_summary="Employee list",
        operation_description="Get employee list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create employee",
        operation_description="Create a new employee",
        request_body=EmployeeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hr', model_code='employee', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EmployeeDetail(BaseRetrieveMixin, BaseUpdateMixin, generics.GenericAPIView):
    queryset = Employee.objects
    serializer_detail = EmployeeDetailSerializer
    serializer_update = EmployeeUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related("user")

    def error_auth_require(self):
        if (
                self.request.method == 'GET' and self.cls_auth_check and self.request.user.employee_current_id and
                self.kwargs.get('pk', None) == str(self.request.user.employee_current_id)
        ):
            self.state_skip_is_admin = True
            result_filter = {
                'id': self.request.user.employee_current_id
            }
            self.cls_auth_check.set_perm_filter_dict(result_filter)
            return result_filter
        return ResponseController.forbidden_403()

    @swagger_auto_schema(
        operation_summary="Employee detail",
        operation_description="Get employee detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee",
        operation_description="Update employee by ID",
        request_body=EmployeeUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EmployeeCompanyList(BaseListMixin, generics.GenericAPIView):
    queryset = Employee.objects

    serializer_list = EmployeeListSerializer
    serializer_detail = EmployeeListSerializer
    list_hidden_field = ['tenant_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'group',
            'user'
        )

    @swagger_auto_schema(
        operation_summary="Employee Company list",
        operation_description="Get employee Company list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class EmployeeTenantList(BaseListMixin, generics.GenericAPIView):
    queryset = Employee.objects

    serializer_list = EmployeeListByOverviewTenantSerializer
    serializer_list_minimal = EmployeeListMinimalByOverviewTenantSerializer
    use_cache_minimal = True
    list_hidden_field = ['tenant_id']
    filterset_fields = {
        'company_id': ['exact', 'in'],
        'user': ['isnull'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'user'
        ).order_by('first_name')

    @swagger_auto_schema(
        operation_summary="Employee Company list",
        operation_description="Get employee Company list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        if request.query_params.get('company_id', None) or request.query_params.get('company_id__in', None):
            return self.list(request, *args, **kwargs)
        raise serializers.ValidationError(
            {
                'detail': HRMsg.FILTER_COMPANY_ID_REQUIRED
            }
        )


class EmployeeMediaToken(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        if request.user.employee_current:
            employee_obj = request.user.employee_current
            access_token = employee_obj.media_access_token
            access_expired = employee_obj.media_access_token_expired
            if access_expired and access_expired > (timezone.now() + timedelta(minutes=10)) and access_token:
                return ResponseController.success_200(
                    data={
                        'access_token': employee_obj.media_access_token
                    }
                )
            refresh_token = employee_obj.media_refresh_token_expired
            refresh_expired = employee_obj.media_refresh_token_expired
            if refresh_token and refresh_expired and refresh_expired > (timezone.now() + timedelta(minutes=10)):
                access_token = APIUtil.get_new_token(
                    media_refresh_token=employee_obj.media_refresh_token,
                    employee_obj=employee_obj,
                )
                if access_token:
                    return ResponseController.success_200(
                        data={
                            'access_token': access_token
                        }
                    )
            access_token = APIUtil.get_new_token_by_login(employee_obj)
            if access_token:
                return ResponseController.success_200(
                    data={
                        'access_token': employee_obj.media_access_token
                    }
                )

        return ResponseController.forbidden_403()
