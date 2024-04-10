from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.models import GroupLevel, Group, Role, Employee
from apps.core.hr.serializers.fimport import (
    GroupImportSerializer, GroupLevelImportReturnSerializer,
    GroupImportReturnSerializer, GroupLevelImportSerializer, RoleImportReturnSerializer, RoleImportSerializer,
    EmployeeImportSerializer, EmployeeImportReturnSerializer,
)
from apps.shared import BaseCreateMixin, mask_view


class GroupLevelImport(BaseCreateMixin):
    queryset = GroupLevel.objects

    serializer_detail = GroupLevelImportReturnSerializer
    serializer_create = GroupLevelImportSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Group Level",
        operation_description="Import new group level",
        request_body=GroupLevelImportSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hr', model_code='group', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_current_id': request.user.company_current_id,
        }
        return self.create(request, *args, **kwargs)


class GroupImport(BaseCreateMixin):
    queryset = Group.objects

    serializer_detail = GroupImportReturnSerializer
    serializer_create = GroupImportSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Group",
        operation_description="Import new group",
        request_body=GroupImportSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hr', model_code='group', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RoleImport(BaseCreateMixin):
    queryset = Role.objects
    serializer_create = RoleImportSerializer
    serializer_detail = RoleImportReturnSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(operation_summary="Import Role", request_body=RoleImportSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EmployeeImport(BaseCreateMixin):
    queryset = Employee.objects
    serializer_detail = EmployeeImportReturnSerializer
    serializer_create = EmployeeImportSerializer
    create_hidden_field = ('tenant_id', 'company_id')

    @swagger_auto_schema(operation_summary="Import employee", request_body=EmployeeImportSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True,
        label_code='hr', model_code='employee', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_obj': request.user.company_current
        }
        return self.create(request, *args, **kwargs)
