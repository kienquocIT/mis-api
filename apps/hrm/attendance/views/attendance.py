# from datetime import datetime

from drf_yasg.utils import swagger_auto_schema

from apps.hrm.attendance.models.attendance import Attendance
from apps.hrm.attendance.serializers.attendance import AttendanceListSerializer, AttendanceDetailSerializer
from apps.shared import BaseListMixin, mask_view


class AttendanceDataList(BaseListMixin):
    queryset = Attendance.objects
    filterset_fields = {
        'employee_id': ['exact', 'in'],
        'date': ['exact', 'gte', 'lte'],
    }
    serializer_list = AttendanceListSerializer
    serializer_detail = AttendanceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    # def get_queryset(self):
    #     date_start = self.request.query_params.get('date_start', '')
    #     date_end = self.request.query_params.get('date_end', '')
    #     employee_id_lst = self.request.query_params.get('employee_id_lst', '').split(',')
    #
    #     if date_start and date_end:
    #         queryset = super().get_queryset().select_related('employee').filter(
    #             employee_id__in=employee_id_lst,
    #             date__gte=datetime.strptime(date_start, "%Y-%m-%d").date(),
    #             date__lte=datetime.strptime(date_end, "%Y-%m-%d").date()
    #         )
    #         return queryset
    #     return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Attendance request list",
        operation_description="get attendance request list"
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
