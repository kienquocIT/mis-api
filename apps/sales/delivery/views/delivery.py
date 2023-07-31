from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin
from apps.sales.delivery.models import OrderDelivery, OrderDeliverySub
from apps.sales.delivery.serializers import OrderDeliveryListSerializer, OrderDeliverySubDetailSerializer, \
    OrderDeliverySubUpdateSerializer

__all__ = ['OrderDeliveryList', 'OrderDeliverySubDetail']


class OrderDeliveryList(BaseListMixin):
    queryset = OrderDelivery.objects
    serializer_list = OrderDeliveryListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary='Order Delivery List',
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OrderDeliverySubDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = OrderDeliverySub.objects
    serializer_detail = OrderDeliverySubDetailSerializer
    serializer_update = OrderDeliverySubUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('orderdeliveryproduct_set')

    @swagger_auto_schema(
        operation_summary='Order Delivery Sub Detail',
        operation_description="Get delivery Sub detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Order Delivery Sub Update',
        operation_description="Put delivery sub detail by ID update done field of product",
        serializer_update=OrderDeliverySubUpdateSerializer
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.update(request, *args, pk, **kwargs)
