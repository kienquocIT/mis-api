from drf_yasg.utils import swagger_auto_schema

from apps.hrm.attendance.models import ShiftAssignment
from apps.hrm.attendance.serializers import ShiftAssignmentListSerializer, ShiftAssignmentCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class ShiftAssignmentList(BaseListMixin, BaseCreateMixin):
    queryset = ShiftAssignment.objects
    filterset_fields = {
        'employee_id': ['exact', 'in'],
        'shift_id': ['exact', 'in'],
        'date': ['exact', 'gte', 'lte'],
    }
    serializer_list = ShiftAssignmentListSerializer
    serializer_detail = ShiftAssignmentListSerializer
    serializer_create = ShiftAssignmentCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
        'employee_created_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee",
            "shift",
        )

    @swagger_auto_schema(
        operation_summary="Shift Assignment List",
        operation_description="Get Shift Assignment List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Shift Assignment",
        operation_description="Create new Shift Assignment",
        request_body=ShiftAssignmentCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
