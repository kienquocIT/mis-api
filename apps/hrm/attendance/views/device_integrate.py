from drf_yasg.utils import swagger_auto_schema

from apps.hrm.attendance.models import DeviceIntegrateEmployee, AttendanceDevice
from apps.hrm.attendance.serializers import DeviceIntegrateEmployeeListSerializer, \
    DeviceIntegrateEmployeeCreateSerializer, DeviceIntegrateEmployeeUpdateSerializer, AttendanceDeviceListSerializer, \
    AttendanceDeviceCreateSerializer, AttendanceDeviceUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseUpdateMixin


class AttendanceDeviceList(BaseListMixin, BaseCreateMixin):
    queryset = AttendanceDevice.objects
    search_fields = ["title", "username", "device_ip"]
    serializer_list = AttendanceDeviceListSerializer
    serializer_detail = AttendanceDeviceListSerializer
    serializer_create = AttendanceDeviceCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    @swagger_auto_schema(
        operation_summary="Attendance Device List",
        operation_description="Get Attendance Device List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Attendance Device",
        operation_description="Create Attendance Device",
        request_body=AttendanceDeviceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AttendanceDeviceDetail(
    BaseUpdateMixin,
):
    queryset = AttendanceDevice.objects
    serializer_detail = AttendanceDeviceListSerializer
    serializer_update = AttendanceDeviceUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update Attendance Device",
        operation_description="Update Attendance Device by ID",
        request_body=AttendanceDeviceUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class DeviceIntegrateEmployeeList(BaseListMixin, BaseCreateMixin):
    queryset = DeviceIntegrateEmployee.objects
    search_fields = ["employee__email", "employee__search_content", "device_employee_id", "device_employee_name"]
    filterset_fields = {
        'employee_id': ['exact', 'in'],
    }
    serializer_list = DeviceIntegrateEmployeeListSerializer
    serializer_detail = DeviceIntegrateEmployeeListSerializer
    serializer_create = DeviceIntegrateEmployeeCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee",
        )

    @swagger_auto_schema(
        operation_summary="Device Integrate Employee List",
        operation_description="Get Device Integrate Employee List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Device Integrate Employee",
        operation_description="Create Device Integrate Employee",
        request_body=DeviceIntegrateEmployeeCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DeviceIntegrateEmployeeDetail(
    BaseUpdateMixin,
):
    queryset = DeviceIntegrateEmployee.objects
    serializer_detail = DeviceIntegrateEmployeeListSerializer
    serializer_update = DeviceIntegrateEmployeeUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update Device Integrate Employee",
        operation_description="Update Device Integrate Employee by ID",
        request_body=DeviceIntegrateEmployeeUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
