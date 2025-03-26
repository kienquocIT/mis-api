from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Product, ProductPriceList
from apps.sales.grouporder.models import GroupOrder
from apps.sales.grouporder.serializers import GroupOrderProductListSerializer, GroupOrderProductPriceListListSerializer, \
    GroupOrderCreateSerializer, GroupOrderListSerializer, GroupOrderDetailSerializer, GroupOrderUpdateSerializer
from apps.shared import (
    mask_view, ResponseController,
    BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin,
)

# Create your views here.
class GroupOrderProductList(BaseListMixin, BaseCreateMixin):
    queryset = Product.objects
    serializer_list = GroupOrderProductListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = [
        'title',
    ]

    def get_queryset(self):
        return super().get_queryset().prefetch_related('bom_product', 'product_price_product')

    @swagger_auto_schema(
        operation_summary="GroupOrder Product list",
        operation_description="GroupOrder Product list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class GroupOrderProductPriceListList(BaseListMixin, BaseCreateMixin):
    queryset = ProductPriceList.objects
    serializer_list = GroupOrderProductPriceListListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = [
        'title',
    ]
    filterset_fields = {
        'product__id': ['exact'],
    }

    def get_queryset(self):
        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="GroupOrder ProductPriceList list",
        operation_description="GroupOrder ProductPriceList list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GroupOrderList(BaseListMixin, BaseCreateMixin):
    queryset = GroupOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = GroupOrderListSerializer
    serializer_create = GroupOrderCreateSerializer
    serializer_detail = GroupOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    @swagger_auto_schema(
        operation_summary="Group Order List",
        operation_description="Get Group Order List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='grouporder', model_code='grouporder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Group Order",
        operation_description="Create New Group Order",
        request_body=GroupOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='grouporder', model_code='grouporder', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class GroupOrderDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GroupOrder.objects
    serializer_detail = GroupOrderDetailSerializer
    serializer_update = GroupOrderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Group Order Detail",
        operation_description="Get Group Order Detail",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='grouporder', model_code='grouporder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Group Order Update",
        operation_description="Group Order Update",
        request_body=GroupOrderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='grouporder', model_code='grouporder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, pk, **kwargs)