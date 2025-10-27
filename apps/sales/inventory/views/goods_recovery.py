from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsRecovery
from apps.sales.inventory.serializers import GoodsRecoveryListSerializer, GoodsRecoveryMinimalListSerializer, \
    GoodsRecoveryCreateSerializer, GoodsRecoveryDetailSerializer, GoodsRecoveryUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsRecoveryList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsRecovery.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = GoodsRecoveryListSerializer
    serializer_list_minimal = GoodsRecoveryMinimalListSerializer
    serializer_create = GoodsRecoveryCreateSerializer
    serializer_detail = GoodsRecoveryDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related("customer", 'employee_created')

    @swagger_auto_schema(
        operation_summary="Goods Recovery List",
        operation_description="Get Goods Recovery List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='leaseorder', model_code='leaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods Recovery",
        operation_description="Create new Goods Recovery",
        request_body=GoodsRecoveryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        employee_require=True,
        # label_code='leaseorder', model_code='leaseorder', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsRecoveryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GoodsRecovery.objects
    serializer_detail = GoodsRecoveryDetailSerializer
    serializer_update = GoodsRecoveryUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Goods Recovery detail",
        operation_description="Get Goods Recovery detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='leaseorder', model_code='leaseorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods Recovery",
        operation_description="Update Goods Recovery by ID",
        request_body=GoodsRecoveryUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='leaseorder', model_code='leaseorder', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
