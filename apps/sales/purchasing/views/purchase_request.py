from drf_yasg.utils import swagger_auto_schema
from apps.sales.purchasing.models import PurchaseRequest, PurchaseRequestProduct
from apps.sales.purchasing.serializers import (
    PurchaseRequestListSerializer, PurchaseRequestCreateSerializer, PurchaseRequestDetailSerializer,
    PurchaseRequestListForPQRSerializer, PurchaseRequestProductListSerializer, PurchaseRequestUpdateSerializer,
    PurchaseRequestSaleListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseRequestList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseRequest.objects
    filterset_fields = {
        'is_all_ordered': ['exact'],
        'system_status': ['exact'],
    }
    search_fields = [
        'title',
        'sale_order__title',
        'supplier__name',
    ]
    serializer_list = PurchaseRequestListSerializer
    serializer_detail = PurchaseRequestDetailSerializer
    serializer_create = PurchaseRequestCreateSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        main_query = super().get_queryset().select_related(
            'supplier',
            'sale_order',
            'distribution_plan',
        )
        return self.get_queryset_custom_direct_page(main_query)

    @swagger_auto_schema(
        operation_summary="Purchase Request List",
        operation_description="Get Purchase Request List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase Request",
        operation_description="Create new Purchase Request",
        request_body=PurchaseRequestCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class PurchaseRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PurchaseRequest.objects
    serializer_detail = PurchaseRequestDetailSerializer
    serializer_update = PurchaseRequestUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
            'sale_order',
            'contact',
            'employee_inherit',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Request detail",
        operation_description="Get Purchase Request detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Purchase Request update",
        operation_description="Update Purchase Request by ID",
        request_body=PurchaseRequestUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchaserequest', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)


class PurchaseRequestListForPQR(BaseListMixin):
    queryset = PurchaseRequest.objects
    serializer_list = PurchaseRequestListForPQRSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().filter(system_status=3).select_related()

    @swagger_auto_schema(
        operation_summary="Purchase Request List For Purchase Quotation Request",
        operation_description="Get Purchase Request List For Purchase Quotation Request",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='purchasing', model_code='purchaserequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PurchaseRequestProductList(BaseListMixin):
    queryset = PurchaseRequestProduct.objects
    filterset_fields = {
        'purchase_request_id': ['in', 'exact'],
    }
    serializer_list = PurchaseRequestProductListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().filter(remain_for_purchase_order__gt=0).select_related(
            'purchase_request',
            'product',
            'product__general_product_category',
            'product__general_uom_group',
            'product__sale_default_uom',
            'product__sale_tax',
            'product__sale_currency_using',
            'product__purchase_default_uom',
            'product__purchase_tax',
            'uom',
            'uom__group',
            'uom__group__uom_reference',
            'tax',
        ).prefetch_related(
            'product__general_product_types_mapped'
        ).order_by('-purchase_request__date_created')

    @swagger_auto_schema(
        operation_summary="Purchase Request Product List",
        operation_description="Get Purchase Request Product List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# PR list use for other apps
class PurchaseRequestSaleList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseRequest.objects
    filterset_fields = {
        'is_all_ordered': ['exact'],
        'system_status': ['exact'],
        'sale_order__opportunity__is_deal_close': ['exact'],
        'request_for': ['exact', 'in'],
    }
    search_fields = [
        'title',
        'sale_order__title',
        'supplier__name',
    ]
    serializer_list = PurchaseRequestSaleListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'sale_order',
            'sale_order__opportunity',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Request For Sale List",
        operation_description="Get Purchase Request For Sale List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
