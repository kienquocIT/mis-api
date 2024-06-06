from drf_yasg.utils import swagger_auto_schema
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.inventory.models import GoodsReturn
from apps.sales.saleorder.models import SaleOrder
from apps.sales.inventory.serializers import (
    SaleOrderListSerializerForGoodsReturn, DeliveryListSerializerForGoodsReturn,
    GoodsReturnListSerializer, GoodsReturnCreateSerializer, GoodsReturnDetailSerializer, GoodsReturnUpdateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsReturnList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsReturn.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = GoodsReturnListSerializer
    serializer_create = GoodsReturnCreateSerializer
    serializer_detail = GoodsReturnDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'sale_order', 'delivery',
        )

    @swagger_auto_schema(
        operation_summary="Goods return List",
        operation_description="Get Goods return List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreturn', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods return",
        operation_description="Create new Goods return",
        request_body=GoodsReturnCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreturn', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsReturnDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GoodsReturn.objects
    serializer_detail = GoodsReturnDetailSerializer
    serializer_update = GoodsReturnUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'sale_order', 'delivery',
        ).prefetch_related(
            'goods_return_product_detail__lot_no',
            'goods_return_product_detail__serial_no',
        )

    @swagger_auto_schema(
        operation_summary="Goods return detail",
        operation_description="Get Goods return detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreturn', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods return",
        operation_description="Update Goods return by ID",
        request_body=GoodsReturnUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreturn', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
