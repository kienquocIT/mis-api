from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from apps.sales.inventory.models import (
    InventoryAdjustment, InventoryAdjustmentItem
)
from apps.sales.inventory.serializers.inventory_adjustment import (
    InventoryAdjustmentListSerializer, InventoryAdjustmentDetailSerializer,
    InventoryAdjustmentCreateSerializer, InventoryAdjustmentUpdateSerializer, InventoryAdjustmentProductListSerializer,
    InventoryAdjustmentOtherListSerializer)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class InventoryAdjustmentList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = InventoryAdjustment.objects
    serializer_list = InventoryAdjustmentListSerializer
    serializer_create = InventoryAdjustmentCreateSerializer
    serializer_detail = InventoryAdjustmentListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Inventory Adjustment List",
        operation_description="Get Inventory Adjustment List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='inventoryadjustment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Inventory Adjustment",
        operation_description="Create new Inventory Adjustment",
        request_body=InventoryAdjustmentCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='inventoryadjustment', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InventoryAdjustmentDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = InventoryAdjustment.objects
    serializer_detail = InventoryAdjustmentDetailSerializer
    serializer_update = InventoryAdjustmentUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'inventory_adjustment_item_mapped__product_mapped',
            'inventory_adjustment_item_mapped__warehouse_mapped',
            'inventory_adjustment_item_mapped__uom_mapped',
            'employees_in_charge_mapped'
        )

    @swagger_auto_schema(
        operation_summary="Inventory Adjustment order detail",
        operation_description="Get Inventory Adjustment detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='inventoryadjustment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Inventory Adjustment",
        operation_description="Update Inventory Adjustment by ID",
        request_body=InventoryAdjustmentUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='inventoryadjustment', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class InventoryAdjustmentProductList(BaseListMixin):
    queryset = InventoryAdjustmentItem.objects
    serializer_list = InventoryAdjustmentProductListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'uom_mapped',
            'product_mapped',
            'warehouse_mapped',
        )

    @swagger_auto_schema(
        operation_summary="Inventory Adjustment Product List",
        operation_description="Get Inventory Adjustment Product List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# Inventory adjustment list use for other apps
class InventoryAdjustmentOtherList(BaseListMixin):
    queryset = InventoryAdjustment.objects
    serializer_list = InventoryAdjustmentOtherListSerializer
    serializer_detail = InventoryAdjustmentOtherListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch(
                'inventory_adjustment_item_mapped',
                queryset=InventoryAdjustmentItem.objects.select_related(
                    'product_mapped',
                    'uom_mapped',
                    'warehouse_mapped',
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Inventory Adjustment Other List",
        operation_description="Get Inventory Adjustment Other List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='inventoryadjustment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
