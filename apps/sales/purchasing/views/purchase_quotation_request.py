from drf_yasg.utils import swagger_auto_schema
from apps.sales.purchasing.models import PurchaseQuotationRequest, PurchaseRequest
from apps.sales.purchasing.serializers import (
    PurchaseQuotationRequestListSerializer, PurchaseQuotationRequestDetailSerializer,
    PurchaseQuotationRequestCreateSerializer, PurchaseQuotationRequestListForPQSerializer,
    PurchaseQuotationRequestUpdateSerializer, PurchaseRequestListForPQRSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseQuotationRequestList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseQuotationRequest.objects
    serializer_list = PurchaseQuotationRequestListSerializer
    serializer_create = PurchaseQuotationRequestCreateSerializer
    serializer_detail = PurchaseQuotationRequestDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        main_query = super().get_queryset().prefetch_related(
            'purchase_request_mapped'
        )
        return self.get_queryset_custom_direct_page(main_query)

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Request List",
        operation_description="Get Purchase Quotation Request List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotationrequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase Quotation Request",
        operation_description="Create new Purchase Quotation Request",
        request_body=PurchaseQuotationRequestCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotationrequest', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class PurchaseQuotationRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PurchaseQuotationRequest.objects
    serializer_detail = PurchaseQuotationRequestDetailSerializer
    serializer_update = PurchaseQuotationRequestUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'purchase_quotation_request__product',
            'purchase_quotation_request__uom__group',
            'purchase_quotation_request__tax',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Request detail",
        operation_description="Get Purchase Quotation Request detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotationrequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Request update",
        operation_description="Update Purchase Quotation Request by ID",
        request_body=PurchaseQuotationRequestUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotationrequest', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.update(request, *args, **kwargs)


class PurchaseQuotationRequestListForPQ(BaseListMixin):
    queryset = PurchaseQuotationRequest.objects
    serializer_list = PurchaseQuotationRequestListForPQSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'purchase_quotation_request__product',
            'purchase_quotation_request__uom',
            'purchase_quotation_request__tax',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Request List For Purchase Quotation",
        operation_description="Get Purchase Quotation Request List For Purchase Quotation",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='purchasing', model_code='purchasequotationrequest', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
