from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.delivery.serializers.delivery import OrderDeliverySubMinimalListSerializer, \
    OrderDeliverySubRecoveryListSerializer
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin
from apps.sales.delivery.models import OrderDeliverySub, OrderDeliveryProduct
from apps.sales.delivery.serializers import OrderDeliverySubDetailSerializer, \
    OrderDeliverySubUpdateSerializer, OrderDeliverySubListSerializer

__all__ = ['OrderDeliverySubList', 'OrderDeliverySubDetail', 'OrderDeliverySubRecoveryList']


class OrderDeliverySubList(BaseListMixin):
    queryset = OrderDeliverySub.objects
    search_fields = ['title', 'code', 'order_delivery__sale_order__title']
    filterset_fields = {
        'order_delivery__sale_order_id': ['exact'],
        'order_delivery__lease_order_id': ['exact'],
    }
    serializer_list = OrderDeliverySubListSerializer
    serializer_list_minimal = OrderDeliverySubMinimalListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        is_minimal = self.get_param(key='is_minimal')
        if is_minimal:
            return super().get_queryset()

        return super().get_queryset().select_related('employee_inherit')

    @swagger_auto_schema(
        operation_summary='Order Delivery List',
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderdeliverysub', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.list(request, *args, **kwargs)


class OrderDeliverySubDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = OrderDeliverySub.objects
    serializer_detail = OrderDeliverySubDetailSerializer
    serializer_update = OrderDeliverySubUpdateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['tenant_id', 'company_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit').prefetch_related(
            Prefetch(
                'delivery_product_delivery_sub',
                queryset=OrderDeliveryProduct.objects.select_related(
                    'product',
                    'uom',
                )
            )

        )

    @swagger_auto_schema(
        operation_summary='Order Delivery Sub Detail',
        operation_description="Get delivery Sub detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderdeliverysub', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Order Delivery Sub Update',
        operation_description="Put delivery sub detail by ID update done field of product",
        serializer_update=OrderDeliverySubUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderdeliverysub', perm_code='edit', )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.update(request, *args, pk, **kwargs)


class OrderDeliverySubRecoveryList(BaseListMixin):
    queryset = OrderDeliverySub.objects
    search_fields = []
    filterset_fields = {
        'order_delivery__sale_order_id': ['exact'],
        'order_delivery__lease_order_id': ['exact'],
    }
    serializer_list = OrderDeliverySubRecoveryListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('delivery_product_delivery_sub')

    @swagger_auto_schema(
        operation_summary='Order Delivery Recovery List',
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
