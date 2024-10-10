from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import ProductWareHouseSerial, ProductWareHouseLot, ProductWareHouse
from apps.sales.inventory.models import GoodsIssue, InventoryAdjustment, GoodsIssueProduct
from apps.sales.inventory.serializers import (
    GoodsIssueListSerializer, GoodsIssueCreateSerializer, GoodsIssueDetailSerializer
)
from apps.sales.inventory.serializers.goods_issue import (
    GoodsIssueUpdateSerializer,
    ProductionOrderListSerializerForGIS,
    ProductionOrderDetailSerializerForGIS,
    InventoryAdjustmentListSerializerForGIS,
    InventoryAdjustmentDetailSerializerForGIS,
    ProductWarehouseSerialListSerializerForGIS,
    ProductWarehouseLotListSerializerForGIS,
    ProductWareHouseListSerializerForGIS, WorkOrderListSerializerForGIS, WorkOrderDetailSerializerForGIS,
    GoodsIssueProductListSerializer
)
from apps.sales.production.models import ProductionOrder, WorkOrder
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class GoodsIssueList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsIssue.objects
    search_fields = ['title']
    serializer_list = GoodsIssueListSerializer
    serializer_create = GoodsIssueCreateSerializer
    serializer_detail = GoodsIssueDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Goods issue List",
        operation_description="Get Goods issue List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Goods issue",
        operation_description="Create new Goods issue",
        request_body=GoodsIssueCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class GoodsIssueDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = GoodsIssue.objects
    serializer_detail = GoodsIssueDetailSerializer
    serializer_update = GoodsIssueUpdateSerializer
    detail_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            "inventory_adjustment",
        ).prefetch_related(
            'goods_issue_product__product',
            'goods_issue_product__uom',
            'goods_issue_product__warehouse'
        )

    @swagger_auto_schema(
        operation_summary="Goods issue detail",
        operation_description="Get Goods issue detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Goods issue",
        operation_description="Update Goods issue by ID",
        request_body=GoodsIssueUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsissue', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)


# related views
class InventoryAdjustmentListForGIS(BaseListMixin):
    queryset = InventoryAdjustment.objects
    serializer_list = InventoryAdjustmentListSerializerForGIS
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(state=2)

    @swagger_auto_schema(
        operation_summary="Inventory Adjustment List For GIS",
        operation_description="Get Inventory Adjustment List For GIS",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='inventoryadjustment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class InventoryAdjustmentDetailForGIS(BaseRetrieveMixin):
    queryset = InventoryAdjustment.objects
    serializer_detail = InventoryAdjustmentDetailSerializerForGIS
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'inventory_adjustment_item_mapped__product_mapped',
            'inventory_adjustment_item_mapped__warehouse_mapped',
            'inventory_adjustment_item_mapped__uom_mapped',
        )

    @swagger_auto_schema(
        operation_summary="Inventory Adjustment order detail For GIS",
        operation_description="Get Inventory Adjustment detail by ID For GIS",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='inventoryadjustment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ProductionOrderListForGIS(BaseListMixin):
    queryset = ProductionOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = ProductionOrderListSerializerForGIS
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter()

    @swagger_auto_schema(
        operation_summary="Production Order List",
        operation_description="Get Production Order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='productionorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductionOrderDetailForGIS(BaseRetrieveMixin):
    queryset = ProductionOrder.objects
    serializer_detail = ProductionOrderDetailSerializerForGIS
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Production Order Detail",
        operation_description="Get Production Order Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='productionorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class WorkOrderListForGIS(BaseListMixin):
    queryset = WorkOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'employee_inherit_id': ['exact'],
        'system_status': ['exact', 'in'],
    }
    serializer_list = WorkOrderListSerializerForGIS
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter()

    @swagger_auto_schema(
        operation_summary="Work Order List",
        operation_description="Get Work Order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='workorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WorkOrderDetailForGIS(BaseRetrieveMixin):
    queryset = WorkOrder.objects
    serializer_detail = WorkOrderDetailSerializerForGIS
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Work Order Detail",
        operation_description="Get Work Order Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='production', model_code='workorder', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class ProductWareHouseListForGIS(BaseListMixin):
    queryset = ProductWareHouse.objects
    serializer_list = ProductWareHouseListSerializerForGIS
    filterset_fields = {
        "id": ["exact"],
        "product_id": ["exact"],
        "warehouse_id": ["exact"],
    }
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(operation_summary='Product WareHouse')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductWareHouseLotListForGIS(BaseListMixin):
    queryset = ProductWareHouseLot.objects
    search_fields = ['lot_number']
    filterset_fields = {
        "product_warehouse_id": ["exact"],
        "product_warehouse__product_id": ["exact"],
        "product_warehouse__warehouse_id": ["exact"],
        "lot_number": ["exact"],
    }
    serializer_list = ProductWarehouseLotListSerializerForGIS
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        if 'detail_list' in self.request.query_params:
            detail_list = self.request.query_params.get('detail_list', '')
            if detail_list:
                return super().get_queryset().filter(id__in=detail_list.split(','))
        return super().get_queryset()

    @swagger_auto_schema(operation_summary='Product WareHouse Lot')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductWareHouseSerialListForGIS(BaseListMixin):
    queryset = ProductWareHouseSerial.objects
    search_fields = ['vendor_serial_number', 'serial_number']
    filterset_fields = {
        "product_warehouse_id": ["exact"],
        "product_warehouse__product_id": ["exact"],
        "product_warehouse__warehouse_id": ["exact"],
        "serial_number": ["exact"],
        "is_delete": ["exact"],
    }
    serializer_list = ProductWarehouseSerialListSerializerForGIS
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        if 'detail_list' in self.request.query_params:
            detail_list = self.request.query_params.get('detail_list', '')
            if detail_list:
                return super().get_queryset().filter(id__in=detail_list.split(','))
        return super().get_queryset()

    @swagger_auto_schema(operation_summary='Product WareHouse Serial For GIS')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GoodsIssueProductList(BaseListMixin, BaseCreateMixin):
    queryset = GoodsIssueProduct.objects
    search_fields = []
    filterset_fields = {
        'goods_issue__production_order_id': ['exact'],
        'goods_issue__work_order_id': ['exact'],
        'goods_issue__system_status': ['exact'],
        'product_id': ['exact'],
    }
    serializer_list = GoodsIssueProductListSerializer

    @swagger_auto_schema(
        operation_summary="Goods Issue Product PR List",
        operation_description="Get Goods Issue Product PR List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
