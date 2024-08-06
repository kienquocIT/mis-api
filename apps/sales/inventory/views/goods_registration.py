from drf_yasg.utils import swagger_auto_schema
from apps.sales.inventory.models import (
    GoodsRegistration,
    GReItemProductWarehouseSerial,
    GReItemProductWarehouseLot,
    GReItemProductWarehouse,
    GReItemBorrow,
    GoodsRegistrationItemSub, GoodsRegistrationItem, NoneGReItemBorrow, NoneGReItemProductWarehouse
)
from apps.sales.inventory.serializers import (
    GoodsRegistrationListSerializer,
    GoodsRegistrationCreateSerializer,
    GoodsRegistrationDetailSerializer,
    GoodsRegistrationUpdateSerializer,
    GReItemProductWarehouseLotSerializer,
    GReItemProductWarehouseSerialSerializer,
    GReItemProductWarehouseSerializer,
    ProjectProductListSerializer,
    GReItemBorrowListSerializer,
    GReItemBorrowCreateSerializer,
    GReItemBorrowDetailSerializer,
    GReItemBorrowUpdateSerializer,
    GoodsRegistrationItemSubSerializer,
    GoodsRegistrationItemAvailableQuantitySerializer, GoodsRegisBorrowListSerializer, NoneGReItemBorrowListSerializer,
    NoneGReItemBorrowCreateSerializer, NoneGReItemBorrowDetailSerializer, NoneGReItemBorrowUpdateSerializer,
    NoneGoodsRegistrationItemAvailableQuantitySerializer
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
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsregistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods registration",
        operation_description="Create new Goods registration",
        request_body=GoodsRegistrationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsregistration', perm_code='create',
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
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsregistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods registration",
        operation_description="Update Goods registration by ID",
        request_body=GoodsRegistrationUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsregistration', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# lấy dữ liệu chi tiết nhập-xuất hàng của dự án
class GoodsRegistrationItemSubList(BaseListMixin):
    queryset = GoodsRegistrationItemSub.objects
    filterset_fields = {'gre_item_id': ['exact']}
    serializer_list = GoodsRegistrationItemSubSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            'warehouse', 'uom', 'gre_item__so_item__sale_order'
        ).order_by(
            'system_date', '-trans_title'
        )

    @swagger_auto_schema(
        operation_summary="Goods registration item sub List",
        operation_description="Get Goods registration item sub List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# lấy hàng đăng kí theo dự án
class GReItemProductWarehouseList(BaseListMixin):
    queryset = GReItemProductWarehouse.objects
    filterset_fields = {
        'gre_item__so_item__sale_order_id': ['exact'],
        'gre_item__product_id': ['exact'],
        'warehouse_id': ['exact'],
    }
    serializer_list = GReItemProductWarehouseSerializer

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


class GReItemProductWarehouseLotList(BaseListMixin):
    queryset = GReItemProductWarehouseLot.objects
    filterset_fields = {
        'gre_item_prd_wh__gre_item__so_item__sale_order_id': ['exact'],
        'gre_item_prd_wh__gre_item__product_id': ['exact'],
        'gre_item_prd_wh__warehouse_id': ['exact'],
    }
    serializer_list = GReItemProductWarehouseLotSerializer

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


class GReItemProductWarehouseSerialList(BaseListMixin):
    queryset = GReItemProductWarehouseSerial.objects
    filterset_fields = {
        'gre_item_prd_wh__gre_item__so_item__sale_order_id': ['exact'],
        'gre_item_prd_wh__gre_item__product_id': ['exact'],
        'gre_item_prd_wh__warehouse_id': ['exact'],
        'sn_registered__is_delete': ['exact'],
    }
    serializer_list = GReItemProductWarehouseSerialSerializer

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


# lấy hàng dự án dành cho Goods Transfer
class ProjectProductList(BaseListMixin):
    queryset = GReItemProductWarehouse.objects
    filterset_fields = {
        'goods_registration__sale_order_id': ['exact'],
        'gre_item__product_id': ['exact']
    }
    serializer_list = ProjectProductListSerializer

    def get_queryset(self):
        if self.request.user.company_current.company_config.cost_per_project:
            return super().get_queryset().select_related(
                'warehouse'
            )
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Project Product List",
        operation_description="Project Products List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# mượn hàng giữa các dự án
class GReItemBorrowList(BaseListMixin, BaseCreateMixin):
    queryset = GReItemBorrow.objects
    filterset_fields = {
        'gre_source_id': ['exact'],
        'gre_item_source_id': ['exact'],
        'gre_source__sale_order_id': ['exact'],
        'gre_item_source__product_id': ['exact'],
    }
    serializer_list = GReItemBorrowListSerializer
    serializer_create = GReItemBorrowCreateSerializer
    serializer_detail = GReItemBorrowDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="Goods registration item borrow List",
        operation_description="Get Goods registration item borrow List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods registration item borrow",
        operation_description="Create new Goods registration item borrow",
        request_body=GReItemBorrowCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GReItemBorrowDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GReItemBorrow.objects
    serializer_detail = GReItemBorrowDetailSerializer
    serializer_update = GReItemBorrowUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Goods registration item borrow detail",
        operation_description="Get Goods return item borrow detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods registration item borrow",
        operation_description="Update Goods registration item borrow by ID",
        request_body=GReItemBorrowUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GoodsRegistrationItemAvailableQuantity(BaseListMixin):
    queryset = GoodsRegistrationItem.objects
    filterset_fields = {
        'so_item__sale_order_id': ['exact'],
        'product_id': ['exact']
    }
    serializer_list = GoodsRegistrationItemAvailableQuantitySerializer

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="Goods registration item available quantity",
        operation_description="Get Goods registration item available quantity",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# mượn hàng từ kho chung
class NoneGReItemBorrowList(BaseListMixin, BaseCreateMixin):
    queryset = NoneGReItemBorrow.objects
    filterset_fields = {
        'gre_source_id': ['exact'],
        'gre_item_source_id': ['exact'],
        'gre_source__sale_order_id': ['exact'],
        'gre_item_source__product_id': ['exact'],
    }
    serializer_list = NoneGReItemBorrowListSerializer
    serializer_create = NoneGReItemBorrowCreateSerializer
    serializer_detail = NoneGReItemBorrowDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="None Goods registration item borrow List",
        operation_description="Get None Goods registration item borrow List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create None Goods registration item borrow",
        operation_description="Create new None Goods registration item borrow",
        request_body=NoneGReItemBorrowCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NoneGReItemBorrowDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = NoneGReItemBorrow.objects
    serializer_detail = NoneGReItemBorrowDetailSerializer
    serializer_update = NoneGReItemBorrowUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="None Goods registration item borrow detail",
        operation_description="None Get Goods return item borrow detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update None Goods registration item borrow",
        operation_description="Update None Goods registration item borrow by ID",
        request_body=NoneGReItemBorrowUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class NoneGoodsRegistrationItemAvailableQuantity(BaseListMixin):
    queryset = NoneGReItemProductWarehouse.objects
    filterset_fields = {
        'warehouse_id': ['exact'],
        'product_id': ['exact']
    }
    serializer_list = NoneGoodsRegistrationItemAvailableQuantitySerializer

    def get_queryset(self):
        return super().get_queryset().select_related()

    @swagger_auto_schema(
        operation_summary="None Goods registration item available quantity",
        operation_description="Get None Goods registration item available quantity",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='GoodsRegistration', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GoodsRegisBorrowList(BaseListMixin):
    queryset = GoodsRegistrationItem.objects
    filterset_fields = {
        'so_item__sale_order_id': ['exact'],
        'product_id': ['exact'],
    }
    serializer_list = GoodsRegisBorrowListSerializer

    # def get_queryset(self):
    #     return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="Goods Registration Borrow List",
        operation_description="Get Goods Registration Borrow List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
