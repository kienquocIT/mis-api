from json import dumps, loads

from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from apps.sales.serviceorder.models import (
    ServiceOrder, ServiceOrderServiceDetail, ServiceOrderWorkOrder, ServiceOrderWorkOrderTask
)
from apps.core.log.models import DocumentLog
from apps.sales.serviceorder.utils.logical_finish import ServiceOrderFinishHandler
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin, \
    ResponseController
from apps.sales.serviceorder.serializers import (
    ServiceOrderListSerializer, ServiceOrderDetailSerializer,
    ServiceOrderCreateSerializer, ServiceOrderUpdateSerializer, ServiceOrderDetailDashboardSerializer,
    SVODeliveryWorkOrderDetailSerializer, ServiceOrderDiffSerializer,
)


__all__ = [
    'ServiceOrderList',
    'ServiceOrderDetail',
    'ServiceOrderDetailDashboard',
    'SVODeliveryWorkOrderDetail',
    'ServiceOrderDiff',
]


class ServiceOrderList(BaseListMixin, BaseCreateMixin):
    queryset = ServiceOrder.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'id': ['exact', 'in'],
        'document_root_id': ['exact', 'in', 'isnull'],
    }
    serializer_list = ServiceOrderListSerializer
    serializer_create = ServiceOrderCreateSerializer
    serializer_detail = ServiceOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        qs = super().get_queryset().select_related("employee_created__group")
        exclude_id = self.request.query_params.get("exclude_id")
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        return qs

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


class ServiceOrderDiff(BaseRetrieveMixin):
    queryset = ServiceOrder.objects
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    serializer_class = ServiceOrderDiffSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    def _get_service_order_snapshot(self, service_order_instance):
        """
        Get the snapshot of a ServiceOrder instance.
        """
        service_order_id_str = str(service_order_instance.id).replace('-', '')
        service_order_doc_log = DocumentLog.objects.filter(app_model_code='serviceorder', app_id=service_order_id_str).first()
        if service_order_doc_log:
            return service_order_doc_log.snapshot

    def _get_service_order_by_id(self, pk: str):
        """
        Get a ServiceOrder instance by ID with proper permission checking.
        """
        field_hidden = self.cls_check.attr.setup_hidden(from_view='retrieve')

        try:
            obj = self.get_queryset().get(
                pk=pk,
                **field_hidden
            )
            # Check object-level permissions
            self.check_object_permissions(self.request, obj)
            return obj
        except ServiceOrder.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary='Service Order Diff - Compare versions',
        operation_description='Get detailed diff between current state and previous version of a ServiceOrder using DeepDiff',
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='serviceorder', model_code='serviceorder', perm_code='view',
    )
    def get(self, request, current_id, comparing_id, *args, **kwargs):
        current_order = self._get_service_order_by_id(current_id)
        if not current_order:
            return ResponseController.notfound_404(f'ServiceOrder with id {current_id} not found.')

        previous_order = self._get_service_order_by_id(comparing_id)
        if not previous_order:
            return ResponseController.notfound_404(f'ServiceOrder with id {comparing_id} not found.')

        # Check permissions for both orders
        if not self.check_perm_by_obj_or_body_data(obj=current_order, auto_check=True):
            return ResponseController.forbidden_403('No permission to access the first ServiceOrder.')

        if not self.check_perm_by_obj_or_body_data(obj=previous_order, auto_check=True):
            return ResponseController.forbidden_403('No permission to access the second ServiceOrder.')

        # Get snapshots for both orders
        current_snapshot = loads(dumps(self._get_service_order_snapshot(current_order)))
        previous_snapshot = loads(dumps(self._get_service_order_snapshot(previous_order)))

        # Prepare data for serializer
        diff_data = {
            'current_snapshot': current_snapshot,
            'previous_snapshot': previous_snapshot,
        }

        # Serialize and return
        serializer = self.serializer_class(diff_data)
        return ResponseController.success_200(
            data=serializer.data,
            key_data='result'
        )
