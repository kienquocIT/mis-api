from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.shared import (
    BaseListMixin, BaseRetrieveMixin,
    mask_view, BaseUpdateMixin, BaseDestroyMixin,
)
from apps.sales.delivery.models import OrderPickingSub, OrderPickingProduct
from apps.sales.delivery.serializers import (
    OrderPickingSubListSerializer,
    OrderPickingSubDetailSerializer, OrderPickingSubUpdateSerializer,
)


__all__ = [
    'OrderPickingSubList',
    'OrderPickingSubDetail',
]


class OrderPickingSubList(BaseListMixin):
    queryset = OrderPickingSub.objects
    search_fields = [
        'order_picking__sale_order__title',
        'code',
    ]
    serializer_list = OrderPickingSubListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit').order_by('-date_created')

    @swagger_auto_schema(
        operation_summary='Order Picking Sub List',
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
        return super().get_queryset().select_related('employee_inherit').prefetch_related(
            Prefetch(
                'picking_product_picking_sub',
                queryset=OrderPickingProduct.objects.select_related(
                    'product',
                    'uom',
                    'product__inventory_uom',
                )
            ),
        )

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
