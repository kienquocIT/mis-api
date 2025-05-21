import hashlib
import uuid
import time
import json
import base64
import requests
from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import ProductWareHouse, Product, ProductWareHouseSerial
from apps.sales.productmodification.serializers import WarehouseListByProductSerializer, ProductModifiedListSerializer, \
    ProductComponentListSerializer, ProductSerialListSerializer
from apps.sales.saleorder.models import SaleOrder
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import ARInvoice, ARInvoiceSign
from apps.sales.arinvoice.serializers import (
    DeliveryListSerializerForARInvoice,
    ARInvoiceListSerializer, ARInvoiceDetailSerializer,
    ARInvoiceCreateSerializer, ARInvoiceUpdateSerializer,
    ARInvoiceSignListSerializer, ARInvoiceSignCreateSerializer,
    ARInvoiceSignDetailSerializer, ARInvoiceRecurrenceListSerializer, SaleOrderListSerializerForARInvoice
)

__all__ = [
    'ProductModifiedList',
    'ProductComponentList',
    'WarehouseListByProduct',
    'ProductSerialList',
]

# related views
class ProductModifiedList(BaseListMixin):
    queryset = Product.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ProductModifiedListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Product Modified List",
        operation_description="Product Modified List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductComponentList(BaseListMixin):
    queryset = Product.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'id': ['exact'],
    }
    serializer_list = ProductComponentListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Product Component List",
        operation_description="Product Component List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WarehouseListByProduct(BaseListMixin):
    queryset = ProductWareHouse.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'product_id': ['exact'],
    }
    serializer_list = WarehouseListByProductSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Warehouse List By Product",
        operation_description="Warehouse List By Product",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProductSerialList(BaseListMixin):
    queryset = ProductWareHouseSerial.objects
    search_fields = [
        'vendor_serial_number',
        'serial_number',
    ]
    filterset_fields = {
        'product_warehouse_id': ['exact'],
    }
    serializer_list = ProductSerialListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Product Serial List",
        operation_description="Product Serial List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
