__all__ = ['OrderDeliveryList']

from drf_yasg.utils import swagger_auto_schema

from ..models import OrderDelivery
from ..serializers import OrderDeliveryListSerializer, OrderPickingDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin

__all__ = ['OrderDeliveryList', 'OrderDeliveryDetail']


class OrderDeliveryList(BaseListMixin):
    queryset = OrderDelivery.objects
    serializer_list = OrderDeliveryListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary='Order Picking List',
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderDeliveryDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
    BaseDestroyMixin
):
    queryset = OrderDelivery.objects
    serializer_detail = OrderDeliveryListSerializer
    serializer_update = OrderPickingDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('sub').prefetch_related('sub__orderdeliveryproduct_set')

    @swagger_auto_schema(
        operation_summary='Order Delivery Detail',
        operation_description="Get delivery detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
