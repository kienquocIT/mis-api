from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.purchasing.models import PurchaseOrder, PurchaseOrderQuotation, PurchaseOrderProduct, \
    PurchaseOrderRequestProduct
from apps.sales.purchasing.serializers.purchase_order import PurchaseOrderCreateSerializer, \
    PurchaseOrderListSerializer, PurchaseOrderUpdateSerializer, PurchaseOrderDetailSerializer, \
    PurchaseOrderSaleListSerializer, PurchaseOrderProductGRListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseOrderList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = PurchaseOrder.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'supplier_id': ['exact'],
        'contact_id': ['exact'],
    }
    serializer_list = PurchaseOrderListSerializer
    serializer_create = PurchaseOrderCreateSerializer
    serializer_detail = PurchaseOrderListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "supplier",
        ).order_by('receipt_status')

    @swagger_auto_schema(
        operation_summary="Purchase order List",
        operation_description="Get Purchase order List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase order",
        operation_description="Create new Purchase order",
        request_body=PurchaseOrderCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaseorder', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PurchaseOrderDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = PurchaseOrder.objects
    serializer_detail = PurchaseOrderDetailSerializer
    serializer_update = PurchaseOrderUpdateSerializer
    update_hidden_field = ['employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "supplier",
            "contact",
        ).prefetch_related(
            'purchase_requests',
            Prefetch(
                'purchase_order_quotation_order',
                queryset=PurchaseOrderQuotation.objects.select_related('purchase_quotation'),
            ),
            Prefetch(
                'purchase_order_request_product_order',
                queryset=PurchaseOrderRequestProduct.objects.select_related(
                    'purchase_request_product',
                    'purchase_request_product__purchase_request',
                    'purchase_request_product__uom',
                ),
            ),
            Prefetch(
                'purchase_order_product_order',
                queryset=PurchaseOrderProduct.objects.select_related(
                    'product',
                    'uom_order_request',
                    'uom_order_request__group',
                    'uom_order_request__group__uom_reference',
                    'uom_order_actual',
                    'uom_order_actual__group',
                    'uom_order_actual__group__uom_reference',
                    'tax',
                ).prefetch_related(
                    Prefetch(
                        'purchase_order_request_order_product',
                        queryset=PurchaseOrderRequestProduct.objects.select_related(
                            'purchase_request_product',
                            'purchase_request_product__purchase_request',
                            'purchase_request_product__uom',
                        )
                    )
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="Purchase order detail",
        operation_description="Get Purchase order detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Purchase order",
        operation_description="Update Purchase order by ID",
        request_body=PurchaseOrderUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaseorder', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PurchaseOrderProductList(BaseListMixin):
    queryset = PurchaseOrderProduct.objects
    filterset_fields = {
        'purchase_order_id': ['in', 'exact'],
    }
    serializer_list = PurchaseOrderProductGRListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().select_related(
            'product',
            'uom_order_request',
            'uom_order_actual',
            'tax',
        ).prefetch_related('purchase_order_request_order_product')

    @swagger_auto_schema(
        operation_summary="Purchase Order Product List",
        operation_description="Get Purchase Order Product List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# use for another sale apps
class PurchaseOrderSaleList(
    BaseListMixin,
    BaseCreateMixin
):
    queryset = PurchaseOrder.objects
    search_fields = ['title']
    filterset_fields = {
        'supplier_id': ['exact'],
        'contact_id': ['exact'],
        'is_all_receipted': ['exact'],
        'system_status': ['exact'],
    }
    serializer_list = PurchaseOrderSaleListSerializer
    serializer_detail = PurchaseOrderSaleListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "supplier",
        ).prefetch_related(
            'purchase_requests'
        )

    @swagger_auto_schema(
        operation_summary="Purchase order sale List",
        operation_description="Get Purchase order sale List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaseorder', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
