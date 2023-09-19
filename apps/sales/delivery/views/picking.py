from drf_yasg.utils import swagger_auto_schema

from apps.shared import (
    BaseListMixin, BaseRetrieveMixin,
    mask_view, BaseUpdateMixin, BaseDestroyMixin,
)
from apps.sales.delivery.models import OrderPicking, OrderPickingSub
from apps.sales.delivery.serializers import (
    OrderPickingListSerializer,
    OrderPickingSubDetailSerializer, OrderPickingSubUpdateSerializer,
)


__all__ = [
    'OrderPickingList',
    'OrderPickingSubDetail',
]


class OrderPickingList(BaseListMixin):
    queryset = OrderPicking.objects
    serializer_list = OrderPickingListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary='Order Picking List',
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderPickingSub', perm_code='view'
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderPickingSubDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
    BaseDestroyMixin
):
    queryset = OrderPickingSub.objects
    serializer_detail = OrderPickingSubDetailSerializer
    serializer_update = OrderPickingSubUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['tenant_id', 'company_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit').prefetch_related('orderpickingproduct_set')

    @swagger_auto_schema(
        operation_summary='Order Picking Sub Detail',
        operation_description="Get picking sub detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderPickingSub', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Order Picking Sub Update',
        operation_description="Update picked quantity (Done) for Order picking product/sub of table",
        serializer_update=OrderPickingSubUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderPickingSub', perm_code='edit'
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
