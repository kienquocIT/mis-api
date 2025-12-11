from drf_yasg.utils import swagger_auto_schema

from apps.hrm.overtimerequest.models import OvertimeRequest
from apps.hrm.overtimerequest.serializers import OvertimeRequestListSerializers, OvertimeRequestDetailSerializers, \
    OvertimeRequestCreateSerializers, OvertimeRequestUpdateSerializers
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class OvertimeRequestList(BaseListMixin, BaseCreateMixin):
    queryset = OvertimeRequest.objects
    serializer_list = OvertimeRequestListSerializers
    serializer_detail = OvertimeRequestDetailSerializers
    serializer_create = OvertimeRequestCreateSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]
    search_fields = ('code', 'title')

    @swagger_auto_schema(
        operation_summary="Overtime request list",
        operation_description="get overtime request list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='overtimeRequest', model_code='overtimeRequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create overtime request",
        operation_description="Create overtime request",
        request_body=OvertimeRequestCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='overtimeRequest', model_code='overtimeRequest', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OvertimeRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = OvertimeRequest.objects
    serializer_detail = OvertimeRequestDetailSerializers
    serializer_update = OvertimeRequestUpdateSerializers
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'ot_map_with_employee_shift__shift',
            'ot_map_with_employee_shift__employee',
        )

    @swagger_auto_schema(
        operation_summary="Overtime request Detail",
        operation_description="get overtime request detail by id",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='overtimeRequest', model_code='overtimeRequest', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Overtime request update",
        operation_description="Overtime request update by ID",
        request_body=OvertimeRequestUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='overtimeRequest', model_code='overtimeRequest', perm_code="edit",
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
