from drf_yasg.utils import swagger_auto_schema

from apps.sales.production.models import ProductionOrder
from apps.sales.production.serializers.production_order import ProductionOrderListSerializer,\
    ProductionOrderCreateSerializer
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