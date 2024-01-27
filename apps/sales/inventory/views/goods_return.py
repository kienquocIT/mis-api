from drf_yasg.utils import swagger_auto_schema
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.saleorder.models import SaleOrder
from apps.sales.inventory.serializers import (
    SaleOrderListSerializerForGoodsReturn, DeliveryListSerializerForGoodsReturn, GetDeliveryProductsDeliveredSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin


class SaleOrderListForGoodsReturn(BaseListMixin, BaseCreateMixin):
    queryset = SaleOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'delivery_call': ['exact'],
        'system_status': ['in'],
        'quotation_id': ['exact'],
        'employee_inherit_id': ['exact', 'in'],
        'employee_inherit__group_id': ['exact', 'in'],
        'opportunity_id': ['exact', 'in'],
    }
    serializer_list = SaleOrderListSerializerForGoodsReturn
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "employee_inherit",
        )

    @swagger_auto_schema(
        operation_summary="Sale Order List",
        operation_description="Get Sale Order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='saleorder', model_code='saleorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.kwargs['system_status'] = 3
        self.kwargs['delivery_status__in'] = [1, 2, 3]
        return self.list(request, *args, **kwargs)


class DeliveryListForGoodsReturn(BaseListMixin):
    queryset = OrderDeliverySub.objects
    serializer_list = DeliveryListSerializerForGoodsReturn
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'order_delivery'
        ).prefetch_related(
            'delivery_product_delivery_sub__product'
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary='Order Delivery List',
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderDeliverySub', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        self.kwargs['state'] = 2
        self.kwargs['sale_order_data__id'] = request.GET.get('sale_order_id')
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


class GetDeliveryProductsDetail(BaseRetrieveMixin):
    queryset = OrderDeliverySub.objects
    serializer_detail = GetDeliveryProductsDeliveredSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    update_hidden_field = ['tenant_id', 'company_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related(
            'delivery_serial_delivery_sub__product_warehouse_serial',
            'delivery_serial_delivery_sub__delivery_product',
            'delivery_lot_delivery_sub__product_warehouse_lot',
            'delivery_lot_delivery_sub__delivery_product'
        )

    @swagger_auto_schema(
        operation_summary='Get Delivery Products',
        operation_description="Get Delivery Products by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderDeliverySub', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
