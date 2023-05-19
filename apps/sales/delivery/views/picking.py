from drf_yasg.utils import swagger_auto_schema

from apps.shared import (
    BaseListMixin, BaseRetrieveMixin,
    mask_view,
)
from apps.sales.delivery.models import OrderPicking
from apps.sales.delivery.serializers import (
    OrderPickingListSerializer,
    OrderPickingDetailSerializer,
)

__all__ = [
    'OrderPickingList',
    'OrderPickingDetail',
]


class OrderPickingList(BaseListMixin):
    queryset = OrderPicking.objects
    serializer_list = OrderPickingListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary='Order Picking List',
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderPickingDetail(BaseRetrieveMixin):
    queryset = OrderPicking.objects
    serializer_detail = OrderPickingDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('sub').prefetch_related('sub__orderpickingproduct_set')

    @swagger_auto_schema(
        operation_summary='Order Picking List',
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
