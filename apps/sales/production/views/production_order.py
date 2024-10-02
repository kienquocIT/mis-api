from drf_yasg.utils import swagger_auto_schema

from apps.sales.production.models import ProductionOrder
from apps.sales.production.serializers.production_order import ProductionOrderListSerializer, \
    ProductionOrderCreateSerializer, ProductionOrderDetailSerializer, ProductionOrderUpdateSerializer, \
    ProductionOrderManualDoneSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class ProductionOrderList(BaseListMixin, BaseCreateMixin):
    queryset = ProductionOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = ProductionOrderListSerializer
    serializer_create = ProductionOrderCreateSerializer
    serializer_detail = ProductionOrderListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Order List",
        operation_description="Get Production Order List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Production Order",
        operation_description="Create New Production Order",
        request_body=ProductionOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionorder', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProductionOrderDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = ProductionOrder.objects
    serializer_detail = ProductionOrderDetailSerializer
    serializer_update = ProductionOrderUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Order Detail",
        operation_description="Get Production Order Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Production Order",
        operation_description="Update Production Order By ID",
        request_body=ProductionOrderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='production', model_code='productionorder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class ProductionOrderDDList(BaseListMixin, BaseCreateMixin):
    queryset = ProductionOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = ProductionOrderDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Production Order DD List",
        operation_description="Get Production Order DD List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductionOrderManualDone(BaseCreateMixin):
    queryset = ProductionOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = ProductionOrderListSerializer
    serializer_create = ProductionOrderManualDoneSerializer
    serializer_detail = ProductionOrderListSerializer
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Manual Done Production Order",
        operation_description="Manual Done Production Order",
        request_body=ProductionOrderManualDoneSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
