from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.arinvoice.serializers import (
    DeliveryListSerializerForARInvoice,
    ARInvoiceListSerializer, ARInvoiceDetailSerializer,
    ARInvoiceCreateSerializer, ARInvoiceUpdateSerializer
)

__all__ = [
    'DeliveryListForARInvoice',
    'ARInvoiceList',
    'ARInvoiceDetail'
]


class ARInvoiceList(BaseListMixin, BaseCreateMixin):
    queryset = ARInvoice.objects
    serializer_list = ARInvoiceListSerializer
    serializer_create = ARInvoiceCreateSerializer
    serializer_detail = ARInvoiceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related(
            'customer_mapped',
            'sale_order_mapped'
        )

    @swagger_auto_schema(
        operation_summary="ARInvoice list",
        operation_description="ARInvoice list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='cashoutflow', model_code='advancepayment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ARInvoice",
        operation_description="Create new ARInvoice",
        request_body=ARInvoiceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='cashoutflow', model_code='advancepayment', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ARInvoiceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ARInvoice.objects  # noqa
    serializer_list = ARInvoiceListSerializer
    serializer_create = ARInvoiceCreateSerializer
    serializer_detail = ARInvoiceDetailSerializer
    serializer_update = ARInvoiceUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'ar_invoice_items__product_mapped',
            'ar_invoice_items__product_mapped_uom',
            'ar_invoice_deliveries__delivery_mapped'
        ).select_related(
            'customer_mapped',
            'sale_order_mapped'
        )

    @swagger_auto_schema(operation_summary='Detail ARInvoice')
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='cashoutflow', model_code='advancepayment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ARInvoice", request_body=ARInvoiceUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='cashoutflow', model_code='advancepayment', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = ARInvoiceUpdateSerializer
        return self.update(request, *args, **kwargs)


class DeliveryListForARInvoice(BaseListMixin):
    queryset = OrderDeliverySub.objects
    serializer_list = DeliveryListSerializerForARInvoice
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().select_related('employee_inherit').prefetch_related(
            'delivery_product_delivery_sub'
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary='Order Delivery List',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='delivery', model_code='orderDeliverySub', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        self.kwargs['state'] = 2
        self.kwargs['sale_order_data__id'] = request.GET.get('sale_order_id')
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)
