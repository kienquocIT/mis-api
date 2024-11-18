from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from apps.hrm.employeeinfo.models import EmployeeInfo, EmployeeHRNotMapEmployeeHRM
from apps.hrm.employeeinfo.serializers import EmployeeInfoListSerializers, EmployeeInfoCreateSerializers, \
    EmployeeInfoUpdateSerializers, EmployeeHRNotMapHRMListSerializers, EmployeeInfoDetailSerializers
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseUpdateMixin, BaseRetrieveMixin


class EmployeeInfoList(BaseListMixin, BaseCreateMixin):
    queryset = EmployeeInfo.objects
    serializer_list = EmployeeInfoListSerializers
    serializer_detail = EmployeeInfoDetailSerializers
    serializer_create = EmployeeInfoCreateSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related('employee', 'employee__user')

    @swagger_auto_schema(
        operation_summary="Employee Info list",
        operation_description="get employee info list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create employee info",
        operation_description="Create employee info",
        request_body=EmployeeInfoCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hrm', model_code='employeeInfo', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_current': request.user.tenant_current,
            'company_current': request.user.company_current,
        }
        return self.create(request, *args, **kwargs)


class EmployeeInfoDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = EmployeeInfo.objects
    serializer_detail = EmployeeInfoDetailSerializers
    serializer_update = EmployeeInfoUpdateSerializers
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('nationality', 'place_of_birth', 'place_of_origin')

    @swagger_auto_schema(
        operation_summary="Employee Info detail",
        operation_description="get employee info detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee info",
        operation_description="Update employee info",
        request_body=EmployeeInfoUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='hrm', model_code='employeeInfo', perm_code='edit'
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class EmployeeNotMapHRMList(BaseListMixin):
    queryset = EmployeeHRNotMapEmployeeHRM.objects
    serializer_list = EmployeeHRNotMapHRMListSerializers
    list_hidden_field = ['company_id']
    filterset_fields = {
        "is_mapped": ["exact"],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'company', 'employee', 'employee__user'
        )

    @swagger_auto_schema(
        operation_summary="Employee not map HRM list",
        operation_description="get Employee not map HRM list",
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_company=True,
        label_code='hrm', model_code='employeeInfo', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
