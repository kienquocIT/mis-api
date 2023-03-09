from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.models import Employee
from apps.core.hr.serializers.employee_serializers import (
    EmployeeListSerializer, EmployeeCreateSerializer,
    EmployeeDetailSerializer, EmployeeUpdateSerializer,
)
from apps.shared import BaseUpdateMixin, mask_view, BaseRetrieveMixin, BaseListMixin, BaseCreateMixin


class EmployeeList(
    BaseListMixin,
    BaseCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Employee.object
    search_fields = ["search_content"]

    serializer_list = EmployeeListSerializer
    serializer_detail = EmployeeListSerializer
    serializer_create = EmployeeCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'user_created']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'group',
            'user'
        ).prefetch_related('role')

    @swagger_auto_schema(
        operation_summary="Employee list",
        operation_description="Get employee list",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create employee",
        operation_description="Create a new employee",
        request_body=EmployeeCreateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EmployeeDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Employee.object
    serializer_detail = EmployeeDetailSerializer
    serializer_update = EmployeeUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("user")

    @swagger_auto_schema(
        operation_summary="Employee detail",
        operation_description="Get employee detail by ID",
    )
    def get(self, request, *args, **kwargs):
        self.serializer_class = EmployeeDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee",
        operation_description="Update employee by ID",
        request_body=EmployeeUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = EmployeeUpdateSerializer
        return self.update(request, *args, **kwargs)
