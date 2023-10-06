from drf_yasg.utils import swagger_auto_schema

from apps.eoffice.leave.models import LeaveRequest
from apps.eoffice.leave.serializers import LeaveRequestListSerializer, LeaveRequestCreateSerializer, \
    LeaveRequestDetailSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin

__all__ = ['LeaveRequestList', 'LeaveRequestDetail']


class LeaveRequestList(BaseListMixin, BaseCreateMixin):
    queryset = LeaveRequest.objects
    serializer_list = LeaveRequestListSerializer
    serializer_detail = LeaveRequestListSerializer
    serializer_create = LeaveRequestCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Leave request list",
        operation_description="get leave request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='eoffice', model_code='leave', perm_code='view',
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
        label_code='eoffice', model_code='leave', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
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
        label_code='eoffice', model_code='leave', perm_code="view",
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
        label_code='eoffice', model_code='leave', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Leave request",
        operation_description="Delete Leave request by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='eoffice', model_code='leave', perm_code="delete",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
