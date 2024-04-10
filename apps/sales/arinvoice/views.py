import hashlib
import uuid
import time
import json
import base64
import requests

from drf_yasg.utils import swagger_auto_schema
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.delivery.models import OrderDeliverySub
from apps.sales.arinvoice.models import ARInvoice, ARInvoiceSign
from apps.sales.arinvoice.serializers import (
    DeliveryListSerializerForARInvoice,
    ARInvoiceListSerializer, ARInvoiceDetailSerializer,
    ARInvoiceCreateSerializer, ARInvoiceUpdateSerializer, ARInvoiceSignListSerializer, ARInvoiceSignCreateSerializer,
    ARInvoiceSignDetailSerializer
)

__all__ = [
    'DeliveryListForARInvoice',
    'ARInvoiceList',
    'ARInvoiceDetail',
    'ARInvoiceSignList'
]


def generate_token(http_method, username, password):
    epoch_start = 0
    timestamp = str(int(time.time() - epoch_start))
    nonce = uuid.uuid4().hex
    signature_raw_data = http_method.upper() + timestamp + nonce

    md5 = hashlib.md5()
    md5.update(signature_raw_data.encode('utf-8'))
    signature = base64.b64encode(md5.digest()).decode('utf-8')

    return f"{signature}:{nonce}:{timestamp}:{username}:{password}"


def update_ar_status():
    ikey_list = []
    all_ar = ARInvoice.objects.all()
    for item in all_ar:
        if item.is_created_einvoice:
            ikey_list.append(str(item.id) + '-' + item.invoice_sign)
    http_method = "POST"
    username = "API"
    password = "Api@0317493763"
    token = generate_token(http_method, username, password)
    headers = {"Authentication": f"{token}", "Content-Type": "application/json"}
    response = requests.post(
        "http://0317493763.softdreams.vn/api/publish/getInvoicesByIkeys",
        headers=headers,
        json={'Ikeys': ikey_list},
        timeout=60
    )
    if response.status_code == 200:
        invoice_info = json.loads(response.text).get('Data', {})['Invoices']
        for ar_obj in all_ar:
            for item in invoice_info:
                if item.get('Ikey') == str(ar_obj.id) + '-' + ar_obj.invoice_sign:
                    ar_obj.invoice_number = item.get('No')
                    ar_obj.invoice_status = item.get('InvoiceStatus')
                    ar_obj.save(update_fields=['invoice_number', 'invoice_status'])
    return True


class ARInvoiceList(BaseListMixin, BaseCreateMixin):
    queryset = ARInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    serializer_list = ARInvoiceListSerializer
    serializer_create = ARInvoiceCreateSerializer
    serializer_detail = ARInvoiceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = [
        'tenant_id', 'company_id',
        'employee_created_id', 'employee_inherit_id',
    ]

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
        login_require=True, auth_require=True,
        label_code='arinvoice', model_code='arinvoice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        if request.query_params.get('update_status'):
            update_ar_status()

        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ARInvoice",
        operation_description="Create new ARInvoice",
        request_body=ARInvoiceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='arinvoice', model_code='arinvoice', perm_code='create',
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
            'ar_invoice_items__product',
            'ar_invoice_items__product_uom',
            'ar_invoice_deliveries__delivery_mapped'
        ).select_related(
            'customer_mapped',
            'sale_order_mapped'
        )

    @swagger_auto_schema(operation_summary='Detail ARInvoice')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='arinvoice', model_code='arinvoice', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ARInvoice", request_body=ARInvoiceUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='arinvoice', model_code='arinvoice', perm_code='edit',
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
        login_require=True, auth_require=True,
        label_code='delivery', model_code='orderDeliverySub', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        self.kwargs['state'] = 2
        self.kwargs['sale_order_data__id'] = request.GET.get('sale_order_id')
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)


class ARInvoiceSignList(BaseListMixin, BaseCreateMixin):
    queryset = ARInvoiceSign.objects
    serializer_list = ARInvoiceSignListSerializer
    serializer_create = ARInvoiceSignCreateSerializer
    serializer_detail = ARInvoiceSignDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="ARInvoiceSign list",
        operation_description="ARInvoiceSign list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create ARInvoiceSign",
        operation_description="Create new ARInvoiceSign",
        request_body=ARInvoiceSignCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_id': request.user.tenant_current_id,
            'company_id': request.user.company_current_id,
        }
        return self.create(request, *args, **kwargs)
