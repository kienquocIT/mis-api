from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderServiceDetail, ServiceOrderWorkOrder, ServiceOrderWorkOrderTask
)
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.serviceorder.serializers import (
    ServiceOrderListSerializer, ServiceOrderDetailSerializer,
    ServiceOrderCreateSerializer, ServiceOrderUpdateSerializer, ServiceOrderDetailDashboardSerializer,
    SVODeliveryWorkOrderDetailSerializer,
)


__all__ = [
    'ServiceOrderList',
    'ServiceOrderDetail',
    'ServiceOrderDetailDashboard',
    'SVODeliveryWorkOrderDetail'
]


class ServiceOrderList(BaseListMixin, BaseCreateMixin):
    queryset = ServiceOrder.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ServiceOrderListSerializer
    serializer_create = ServiceOrderCreateSerializer
    serializer_detail = ServiceOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related("employee_created__group")

    @swagger_auto_schema(
        operation_summary="ServiceOrder list",
        operation_description="ServiceOrder list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='serviceorder', model_code='serviceorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ServiceOrder",
        operation_description="Create new ServiceOrder",
        request_body=ServiceOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='serviceorder', model_code='serviceorder', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class ServiceOrderDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ServiceOrder.objects  # noqa
    serializer_list = ServiceOrderListSerializer
    serializer_detail = ServiceOrderDetailSerializer
    serializer_update = ServiceOrderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "employee_inherit",
        ).prefetch_related(
            Prefetch(
                'service_details',
                queryset=ServiceOrderServiceDetail.objects.select_related('product'),
            ),
            Prefetch(
                'work_orders',
                queryset=ServiceOrderWorkOrder.objects.select_related(
                    'product',
                ).prefetch_related(
                    'work_order_costs',
                    'work_order_contributions',
                    Prefetch(
                        'service_order_work_order_task_wo',
                        queryset=ServiceOrderWorkOrderTask.objects.select_related(
                            'task__employee_created',
                            'task__employee_inherit',
                        ),
                    ),
                ),
            ),
            "service_order_shipment_service_order",
            "attachment_m2m",
            "payments",
            "service_order_expense_service_order"
        )

    @swagger_auto_schema(operation_summary='Detail ServiceOrder')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='serviceorder', model_code='serviceorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ServiceOrder", request_body=ServiceOrderUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='serviceorder', model_code='serviceorder', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)


class ServiceOrderDetailDashboard(BaseRetrieveMixin):
    queryset = ServiceOrder.objects  # noqa
    serializer_detail = ServiceOrderDetailDashboardSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Service Order Detail Dashboard')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='serviceorder', model_code='serviceorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class SVODeliveryWorkOrderDetail(BaseListMixin):
    queryset = ServiceOrderWorkOrder.objects
    serializer_list = SVODeliveryWorkOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        if 'service_order_id' in self.request.query_params:
            return super().get_queryset().filter(
                service_order_id=self.request.query_params.get('service_order_id'),
                is_delivery_point=True
            )
        return super().get_queryset().none()

    @swagger_auto_schema(operation_summary="Delivery Service Work Order Detail")
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
