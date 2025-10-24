from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.delivery.serializers.delivery import DeliveryProductLeaseListSerializer, OrderDeliverySubPrintSerializer
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin
from apps.sales.delivery.models import OrderDeliverySub, OrderDeliveryProduct
from apps.sales.delivery.serializers import OrderDeliverySubDetailSerializer, \
    OrderDeliverySubUpdateSerializer, OrderDeliverySubListSerializer, OrderDeliverySubMinimalListSerializer, \
    OrderDeliverySubRecoveryListSerializer

__all__ = [
    'OrderDeliverySubList',
    'OrderDeliverySubDetail',
    'OrderDeliverySubRecoveryList',
    'DeliveryProductLeaseList',
    'OrderDeliverySubDetailPrint',
    'DeliveryWorkLogList',
]


class OrderDeliverySubList(BaseListMixin):
    queryset = OrderDeliverySub.objects
    search_fields = ['title', 'code', 'order_delivery__sale_order__title']
    filterset_fields = {
        'order_delivery__sale_order_id': ['exact'],
        'order_delivery__lease_order_id': ['exact'],
        'system_status': ['exact'],
        'state': ['exact'],
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
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = ['tenant_id', 'company_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'employee_inherit',
            'sale_order',
        ).prefetch_related(
            Prefetch(
                'delivery_product_delivery_sub',
                queryset=OrderDeliveryProduct.objects.select_related(
                    'product',
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


# PRINT VIEW
class OrderDeliverySubDetailPrint(
    BaseRetrieveMixin,
):
    queryset = OrderDeliverySub.objects
    serializer_detail = OrderDeliverySubPrintSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = ['tenant_id', 'company_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'employee_inherit',
            'sale_order',
        ).prefetch_related(
            Prefetch(
                'delivery_product_delivery_sub',
                queryset=OrderDeliveryProduct.objects.select_related(
                    'product',
                )
            )

        )

    @swagger_auto_schema(
        operation_summary='Order Delivery Sub Print Detail',
        operation_description="Get delivery Sub print Detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderdeliverysub', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


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


class DeliveryProductLeaseList(BaseListMixin):
    queryset = OrderDeliveryProduct.objects
    filterset_fields = {
        'id': ['exact', 'in'],
        'delivery_sub__order_delivery__lease_order_id': ['exact', 'in'],
        'delivery_sub__system_status': ['exact'],
    }
    serializer_list = DeliveryProductLeaseListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'delivery_pt_delivery_product',
            'delivery_pa_delivery_product',
        )

    @swagger_auto_schema(
        operation_summary="Delivery Product Lease List",
        operation_description="Get Delivery Product Lease List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DeliveryWorkLogList(BaseListMixin):
    queryset = OrderDeliverySub.objects
    filterset_fields = {
        'service_order__document_root_id': ['exact', 'in'],
    }
    serializer_list = OrderDeliverySubDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Delivery Work Log List",
        operation_description="Get Delivery Work Log List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
