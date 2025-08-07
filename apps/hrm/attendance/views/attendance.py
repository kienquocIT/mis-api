from drf_yasg.utils import swagger_auto_schema

from apps.hrm.attendance.models.attendance import Attendance
from apps.hrm.attendance.serializers.attendance import AttendanceListSerializer, AttendanceDetailSerializer, \
    AttendanceCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class AttendanceDataList(BaseListMixin, BaseCreateMixin):
    queryset = Attendance.objects
    filterset_fields = {
        'employee_id': ['exact', 'in'],
        'date': ['exact', 'gte', 'lte'],
    }
    serializer_list = AttendanceListSerializer
    serializer_detail = AttendanceListSerializer
    serializer_create = AttendanceCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Attendance request list",
        operation_description="get attendance request list"
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Assignment",
        operation_description="Create new Assignments",
        request_body=AttendanceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
