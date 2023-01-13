from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.shared import mask_view
from apps.shared.mixins import BaseListMixin

from apps.core.hr.mixins import HRListMixin, HRCreateMixin, HRUpdateMixin, HRRetrieveMixin
from apps.core.hr.models import Employee
from apps.core.hr.serializers.employee_serializers import EmployeeListSerializer, EmployeeCreateSerializer, \
    EmployeeDetailSerializer, EmployeeUpdateSerializer, EmployeeListByCompanyOverviewSerializer


class EmployeeList(
    HRListMixin,
    HRCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Employee.object_global
    search_fields = ["search_content"]

    serializer_class = EmployeeListSerializer
    serializer_create = EmployeeCreateSerializer

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
    HRRetrieveMixin,
    HRUpdateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related(
        "user",
    )
    serializer_class = EmployeeDetailSerializer
    serializer_update = EmployeeUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Employee detail",
        operation_description="Get employee detail by ID",
    )
    def get(self, request, *args, **kwargs):
        self.serializer_class = EmployeeDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update employee",
        operation_description="Update employee information by ID",
        request_body=EmployeeUpdateSerializer,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class EmployeeUserByCompanyOverviewDetail(BaseListMixin):
    queryset = Employee.object_normal.all()
    serializer_list = EmployeeListByCompanyOverviewSerializer
    list_hidden_field = ['tenant_id']
    filterset_fields = {
        "user": ["isnull", "exact"],
    }

    @swagger_auto_schema(operation_summary="Employee List for Company Overview")
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
