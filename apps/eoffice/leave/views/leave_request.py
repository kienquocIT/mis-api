from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.leave.models import LeaveRequest, LeaveAvailable, LeaveAvailableHistory
from apps.eoffice.leave.serializers import LeaveRequestListSerializer, LeaveRequestCreateSerializer, \
    LeaveRequestDetailSerializer
from apps.eoffice.leave.serializers.leave_request import LeaveAvailableListSerializer, LeaveAvailableEditSerializer, \
    LeaveAvailableHistoryListSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin

__all__ = ['LeaveRequestList', 'LeaveRequestDetail', 'LeaveAvailableList', 'LeaveAvailableUpdate',
           'LeaveAvailableHistoryList']


class LeaveRequestList(BaseListMixin, BaseCreateMixin):
    queryset = LeaveRequest.objects
    serializer_list = LeaveRequestListSerializer
    serializer_detail = LeaveRequestListSerializer
    serializer_create = LeaveRequestCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]
    search_fields = ('code', 'title')

    @swagger_auto_schema(
        operation_summary="Leave request list",
        operation_description="get leave request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaverequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create leave request",
        operation_description="Create new leave request",
        request_body=LeaveRequestCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaverequest', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
            'employee_id': request.user.employee_current_id,
        }
        return self.create(request, *args, **kwargs)


class LeaveRequestDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = LeaveRequest.objects
    serializer_detail = LeaveRequestDetailSerializer
    serializer_update = LeaveRequestDetailSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Leave request detail",
        operation_description="Get detail leave request by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaverequest', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Leave request",
        operation_description="Update Leave request by ID",
        request_body=LeaveRequestDetailSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaverequest', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Leave request",
        operation_description="Delete Leave request by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaverequest', perm_code="delete",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LeaveAvailableList(BaseListMixin):
    queryset = LeaveAvailable.objects
    serializer_list = LeaveAvailableListSerializer
    filterset_fields = ('check_balance', 'employee_inherit_id')

    def get_queryset(self):
        return super().get_queryset().select_related('leave_type')

    @swagger_auto_schema(
        operation_summary="Leave available list",
        operation_description="get leave available list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaveavailable', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LeaveAvailableUpdate(BaseUpdateMixin):
    queryset = LeaveAvailable.objects
    serializer_update = LeaveAvailableEditSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update Leave available",
        operation_description="Update Leave available by ID",
        request_body=LeaveAvailableEditSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaveavailable', perm_code="view",
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_id': request.user.employee_current_id,
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.update(request, *args, **kwargs)


class LeaveAvailableHistoryList(BaseListMixin):
    queryset = LeaveAvailableHistory.objects
    serializer_list = LeaveAvailableHistoryListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('leave_available').prefetch_related('leave_available__leave_type')

    @swagger_auto_schema(
        operation_summary="Leave available history list",
        operation_description="get leave available history list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='leave', model_code='leaveavailable', perm_code='view',
    )
    def get(self, request, *args, employee_inherit_id, **kwargs):
        return self.list(request, *args, employee_inherit_id, **kwargs)
