from drf_yasg.utils import swagger_auto_schema
from apps.masterdata.saledata.models import (
    Product, ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial
)
from apps.sales.equipmentloan.models import EquipmentLoan
from apps.sales.equipmentloan.serializers import (
    ELProductListSerializer, ELWarehouseListByProductSerializer,
    ELProductLotListSerializer, ELProductSerialListSerializer,
    EquipmentLoanListSerializer, EquipmentLoanCreateSerializer,
    EquipmentLoanDetailSerializer, EquipmentLoanUpdateSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, mask_view


__all__ = [
    'EquipmentLoanList',
    'EquipmentLoanDetail',
    'ELProductList',
    'ELWarehouseListByProduct',
    'ELProductLotList',
    'ELProductSerialList',
]

# main
class EquipmentLoanList(BaseListMixin, BaseCreateMixin):
    queryset = EquipmentLoan.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = EquipmentLoanListSerializer
    serializer_create = EquipmentLoanCreateSerializer
    serializer_detail = EquipmentLoanDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Equipment Loan list",
        operation_description="Equipment Loan list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentloan', model_code='equipmentloan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Product Modification",
        operation_description="Create new Product Modification",
        request_body=EquipmentLoanCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentloan', model_code='equipmentloan', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class EquipmentLoanDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = EquipmentLoan.objects  # noqa
    serializer_detail = EquipmentLoanDetailSerializer
    serializer_update = EquipmentLoanUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail Equipment Loan')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentloan', model_code='equipmentloan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Product Modification", request_body=EquipmentLoanUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='equipmentloan', model_code='equipmentloan', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)

# related
class ELProductList(BaseListMixin):
    queryset = Product.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ELProductListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Loan Product List",
        operation_description="Loan Product List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ELWarehouseListByProduct(BaseListMixin):
    queryset = ProductWareHouse.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'product_id': ['exact'],
    }
    serializer_list = ELWarehouseListByProductSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Warehouse List By Product",
        operation_description="Warehouse List By Product",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ELProductLotList(BaseListMixin):
    queryset = ProductWareHouseLot.objects
    search_fields = [
        'lot_number',
    ]
    filterset_fields = {
        'product_warehouse__product_id': ['exact'],
        'product_warehouse__warehouse_id': ['exact'],
    }
    serializer_list = ELProductLotListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Product Lot List",
        operation_description="Product Lot List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ELProductSerialList(BaseListMixin):
    queryset = ProductWareHouseSerial.objects
    search_fields = [
        'vendor_serial_number',
        'serial_number',
    ]
    filterset_fields = {
        'product_warehouse__product_id': ['exact'],
        'product_warehouse__warehouse_id': ['exact'],
    }
    serializer_list = ELProductSerialListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(serial_status=0)

    @swagger_auto_schema(
        operation_summary="Product Serial List",
        operation_description="Product Serial List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
