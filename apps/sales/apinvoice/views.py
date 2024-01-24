from drf_yasg.utils import swagger_auto_schema

from apps.sales.inventory.models import GoodsReceipt
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.apinvoice.serializers import (
    GoodsReceiptListSerializerForAPInvoice, APInvoiceListSerializer, APInvoiceCreateSerializer,
    APInvoiceDetailSerializer, APInvoiceUpdateSerializer
)
from apps.sales.apinvoice.models import APInvoice

__all__ = [
    'GoodsReceiptListForAPInvoice', 'APInvoiceList', 'APInvoiceDetail'
]


class APInvoiceList(BaseListMixin, BaseCreateMixin):
    queryset = APInvoice.objects
    serializer_list = APInvoiceListSerializer
    serializer_create = APInvoiceCreateSerializer
    serializer_detail = APInvoiceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related(
            'supplier_mapped',
            'po_mapped'
        )

    @swagger_auto_schema(
        operation_summary="ARInvoice list",
        operation_description="ARInvoice list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='arinvoice', model_code='arinvoice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ARInvoice",
        operation_description="Create new ARInvoice",
        request_body=APInvoiceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='arinvoice', model_code='arinvoice', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class APInvoiceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = APInvoice.objects  # noqa
    serializer_list = APInvoiceListSerializer
    serializer_create = APInvoiceCreateSerializer
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
            'po_mapped'
        )

    @swagger_auto_schema(operation_summary='Detail ARInvoice')
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='arinvoice', model_code='arinvoice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ARInvoice", request_body=APInvoiceUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='arinvoice', model_code='arinvoice', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = APInvoiceUpdateSerializer
        return self.update(request, *args, **kwargs)


class GoodsReceiptListForAPInvoice(BaseListMixin):
    queryset = GoodsReceipt.objects
    serializer_list = GoodsReceiptListSerializerForAPInvoice
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "purchase_order",
            "inventory_adjustment",
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary='Order Delivery List',
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='inventory', model_code='goodsreceipt', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        self.kwargs['system_status'] = 3
        self.kwargs['purchase_order_id'] = request.GET.get('purchase_order_id')
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)
