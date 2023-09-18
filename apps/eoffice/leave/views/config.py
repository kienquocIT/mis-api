__all__ = ['LeaveConfigDetail']

from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.leave.mixins import LeaveDestroyMixin
from apps.eoffice.leave.models import LeaveConfig, LeaveType
from apps.eoffice.leave.serializers import LeaveConfigDetailSerializer, LeaveTypeConfigCreateSerializer,\
    LeaveTypeConfigUpdateSerializer, LeaveTypeConfigDetailSerializer, LeaveTypeConfigDeleteSerializer
from apps.shared import BaseRetrieveMixin, BaseUpdateMixin, mask_view, BaseCreateMixin, BaseDestroyMixin

__all__ = ['LeaveConfigDetail', 'LeaveTypeConfigCreate', 'LeaveTypeConfigUpdate']


class LeaveConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = LeaveConfig.objects
    serializer_detail = LeaveConfigDetailSerializer
    serializer_update = LeaveConfigDetailSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="leave Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        self.ser_context = {
            'company_id': request.user.company_current_id
        }
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Leave Config Update",
        request_body=LeaveConfigDetailSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='delivery', model_code='orderdiliverysub', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class LeaveTypeConfigCreate(BaseCreateMixin, BaseRetrieveMixin):
    queryset = LeaveType.objects
    serializer_create = LeaveTypeConfigCreateSerializer
    serializer_detail = LeaveTypeConfigDetailSerializer
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Leave Type Create",
        request_body=LeaveTypeConfigCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_company=True
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LeaveTypeConfigUpdate(BaseUpdateMixin, LeaveDestroyMixin):
    queryset = LeaveType.objects
    serializer_update = LeaveTypeConfigUpdateSerializer
    serializer_delete = LeaveTypeConfigDeleteSerializer
    create_hidden_field = ['company_id']

    @swagger_auto_schema(
        operation_summary="Leave Type Update",
        request_body=LeaveTypeConfigUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_company=True
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Leave Type Delete",
        serializer_delete=LeaveTypeConfigDeleteSerializer
    )
    @mask_view(
        login_require=True, auth_require=True, allow_admin_company=True
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
