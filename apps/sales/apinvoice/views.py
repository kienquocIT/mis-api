from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsReceipt
from apps.sales.purchasing.models import PurchaseOrder
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.apinvoice.serializers import (
    GoodsReceiptListSerializerForAPInvoice, APInvoiceListSerializer, APInvoiceCreateSerializer,
    APInvoiceDetailSerializer, APInvoiceUpdateSerializer, PurchaseOrderListSerializerForAPInvoice
)
from apps.sales.apinvoice.models import APInvoice


__all__ = [
    'GoodsReceiptListForAPInvoice', 'APInvoiceList', 'APInvoiceDetail'
]


class APInvoiceList(BaseListMixin, BaseCreateMixin):
    queryset = APInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'purchase_order_mapped__purchase_requests__request_for': ['exact']
    }
    serializer_list = APInvoiceListSerializer
    serializer_create = APInvoiceCreateSerializer
    serializer_detail = APInvoiceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id', 'employee_inherit_id',
    ]

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related(
            'supplier_mapped',
            'purchase_order_mapped'
        )

    @swagger_auto_schema(
        operation_summary="ARInvoice list",
        operation_description="ARInvoice list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='apinvoice', model_code='apinvoice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ARInvoice",
        operation_description="Create new ARInvoice",
        request_body=APInvoiceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='apinvoice', model_code='apinvoice', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class APInvoiceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = APInvoice.objects  # noqa
    serializer_list = APInvoiceListSerializer
    serializer_detail = APInvoiceDetailSerializer
    serializer_update = APInvoiceUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'ap_invoice_items__product',
            'ap_invoice_items__product_uom',
            'ap_invoice_goods_receipts__goods_receipt_mapped'
        ).select_related(
            'supplier_mapped',
            'purchase_order_mapped'
        )

    @swagger_auto_schema(operation_summary='Detail ARInvoice')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='apinvoice', model_code='apinvoice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ARInvoice", request_body=APInvoiceUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='apinvoice', model_code='apinvoice', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)


# related views
class PurchaseOrderListForAPInvoice(BaseListMixin):
    queryset = PurchaseOrder.objects
    search_fields = ['title', 'code', 'supplier__name']
    filterset_fields = {
        'supplier_id': ['exact'],
    }
    serializer_list = PurchaseOrderListSerializerForAPInvoice
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().filter(
            system_status=3
        ).select_related()

    @swagger_auto_schema(
        operation_summary="PurchaseOrder List",
        operation_description="Get PurchaseOrder List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GoodsReceiptListForAPInvoice(BaseListMixin):
    queryset = GoodsReceipt.objects
    serializer_list = GoodsReceiptListSerializerForAPInvoice
    filterset_fields = {
        'purchase_order_id': ['exact'],
    }
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().filter(
            system_status=3
        ).select_related().prefetch_related(
            'goods_receipt_product_goods_receipt'
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary='Order Delivery List',
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='inventory', model_code='goodsreceipt', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
