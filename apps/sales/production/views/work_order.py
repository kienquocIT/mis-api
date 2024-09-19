from drf_yasg.utils import swagger_auto_schema

from apps.sales.production.models import WorkOrder
from apps.sales.production.serializers.work_order import WorkOrderListSerializer, WorkOrderCreateSerializer, \
    WorkOrderDetailSerializer, WorkOrderUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class WorkOrderList(BaseListMixin, BaseCreateMixin):
    queryset = WorkOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = WorkOrderListSerializer
    serializer_create = WorkOrderCreateSerializer
    serializer_detail = WorkOrderListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Work Order List",
        operation_description="Get Work Order List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='workorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Work Order",
        operation_description="Create New Work Order",
        request_body=WorkOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='workorder', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkOrderDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = WorkOrder.objects
    serializer_detail = WorkOrderDetailSerializer
    serializer_update = WorkOrderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Work Order Detail",
        operation_description="Get Work Order Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='workorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Work Order",
        operation_description="Update Work Order By ID",
        request_body=WorkOrderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='workorder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class WorkOrderDDList(BaseListMixin, BaseCreateMixin):
    queryset = WorkOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = WorkOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Work Order DD List",
        operation_description="Get Work Order DD List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
