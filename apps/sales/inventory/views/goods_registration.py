from drf_yasg.utils import swagger_auto_schema
from apps.sales.inventory.models import (
    GoodsRegistration,
    GoodsRegistrationSerial,
    GoodsRegistrationLot, GoodsRegistrationGeneral
)
from apps.sales.inventory.serializers import (
    GoodsRegistrationListSerializer,
    GoodsRegistrationCreateSerializer,
    GoodsRegistrationDetailSerializer,
    GoodsRegistrationUpdateSerializer,
    GoodsRegistrationLotSerializer,
    GoodsRegistrationSerialSerializer, GoodsRegistrationGeneralSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsRegistrationList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsRegistration.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = GoodsRegistrationListSerializer
    serializer_create = GoodsRegistrationCreateSerializer
    serializer_detail = GoodsRegistrationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="Goods registration List",
        operation_description="Get Goods registration List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods registration",
        operation_description="Create new Goods registration",
        request_body=GoodsRegistrationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GoodsRegistrationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GoodsRegistration.objects
    serializer_detail = GoodsRegistrationDetailSerializer
    serializer_update = GoodsRegistrationUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Goods registration detail",
        operation_description="Get Goods return detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods registration",
        operation_description="Update Goods registration by ID",
        request_body=GoodsRegistrationUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GoodsRegistrationGeneralList(BaseListMixin):
    queryset = GoodsRegistrationGeneral.objects
    filterset_fields = {
        'gre_item__so_item__sale_order_id': ['exact'],
        'gre_item__product_id': ['exact'],
        'warehouse_id': ['exact'],
    }
    serializer_list = GoodsRegistrationGeneralSerializer

    def get_queryset(self):
        if self.request.user.company_current.company_config.cost_per_project:
            return super().get_queryset().select_related(
                'warehouse'
            )
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Goods registration Lot List",
        operation_description="Get Goods registration Lot List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GoodsRegistrationLotList(BaseListMixin):
    queryset = GoodsRegistrationLot.objects
    filterset_fields = {
        'gre_general__gre_item__so_item__sale_order_id': ['exact'],
        'gre_general__gre_item__product_id': ['exact'],
        'gre_general__warehouse_id': ['exact'],
    }
    serializer_list = GoodsRegistrationLotSerializer

    def get_queryset(self):
        if self.request.user.company_current.company_config.cost_per_project:
            return super().get_queryset().select_related(
                'lot_registered'
            )
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Goods registration Lot List",
        operation_description="Get Goods registration Lot List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GoodsRegistrationSerialList(BaseListMixin):
    queryset = GoodsRegistrationSerial.objects
    filterset_fields = {
        'gre_general__gre_item__so_item__sale_order_id': ['exact'],
        'gre_general__gre_item__product_id': ['exact'],
        'gre_general__warehouse_id': ['exact'],
        'sn_registered__is_delete': ['exact'],
    }
    serializer_list = GoodsRegistrationSerialSerializer

    def get_queryset(self):
        if self.request.user.company_current.company_config.cost_per_project:
            return super().get_queryset().select_related(
                'sn_registered'
            )
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Goods registration Serial List",
        operation_description="Get Goods registration Serial List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
