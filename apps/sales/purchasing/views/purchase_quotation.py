from drf_yasg.utils import swagger_auto_schema
from apps.sales.purchasing.models import PurchaseQuotation, PurchaseQuotationProduct
from apps.sales.purchasing.serializers import (
    PurchaseQuotationListSerializer, PurchaseQuotationDetailSerializer,
    PurchaseQuotationCreateSerializer, PurchaseQuotationProductListSerializer,
    PurchaseQuotationUpdateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseQuotationList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseQuotation.objects
    search_fields = [
        'title',
        'code',
        'supplier_mapped__name',
        'purchase_quotation_request_mapped__title',
        'purchase_quotation_request_mapped__code',
    ]
    filterset_fields = {
        'purchase_quotation_request_mapped__purchase_request_mapped__id': ['in', 'exact'],
        'supplier_mapped_id': ['exact'],
    }
    serializer_list = PurchaseQuotationListSerializer
    serializer_create = PurchaseQuotationCreateSerializer
    serializer_detail = PurchaseQuotationDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        # Check filter parameters in the request
        data_filter = self.request.query_params.dict()
        if 'purchase_quotation_request_mapped__purchase_request_mapped__id__in' in data_filter:
            return super().get_queryset().select_related(
                'purchase_quotation_request_mapped',
                'supplier_mapped__owner',
            ).distinct()
        return super().get_queryset().select_related('purchase_quotation_request_mapped', 'supplier_mapped__owner')

    @swagger_auto_schema(
        operation_summary="Purchase Quotation List",
        operation_description="Get Purchase Quotation List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase Quotation Request",
        operation_description="Create new Purchase Quotation Request",
        request_body=PurchaseQuotationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotation', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PurchaseQuotationDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = PurchaseQuotation.objects
    serializer_detail = PurchaseQuotationDetailSerializer
    serializer_update = PurchaseQuotationUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier_mapped',
            'contact_mapped',
            'purchase_quotation_request_mapped'
        ).prefetch_related(
            'purchase_quotation__uom',
            'purchase_quotation__tax',
            'purchase_quotation__product',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Quotation detail",
        operation_description="Get Purchase Quotation detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Purchase Quotation update",
        operation_description="Update Purchase Quotation by ID",
        request_body=PurchaseQuotationUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='purchasing', model_code='purchasequotation', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class PurchaseQuotationProductList(BaseListMixin):
    queryset = PurchaseQuotationProduct.objects
    filterset_fields = {
        'purchase_quotation_id': ['in', 'exact'],
    }
    serializer_list = PurchaseQuotationProductListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().select_related(
            'purchase_quotation',
            'uom',
            'uom__group'
        ).order_by('-purchase_quotation__date_created')

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Product List",
        operation_description="Get Purchase Quotation Product List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# PQ list use for other apps
class PurchaseQuotationSaleList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseQuotation.objects
    search_fields = [
        'title',
        'code',
        'supplier_mapped__name',
        'purchase_quotation_request_mapped__title',
        'purchase_quotation_request_mapped__code',
    ]
    filterset_fields = {
        'purchase_quotation_request_mapped__purchase_request_mapped__id': ['in', 'exact'],
        'supplier_mapped_id': ['exact'],
    }
    serializer_list = PurchaseQuotationListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        # Check filter parameters in the request
        data_filter = self.request.query_params.dict()
        if 'purchase_quotation_request_mapped__purchase_request_mapped__id__in' in data_filter:
            return super().get_queryset().select_related(
                'purchase_quotation_request_mapped',
                'supplier_mapped__owner',
            ).distinct()
        return super().get_queryset().select_related('purchase_quotation_request_mapped', 'supplier_mapped__owner')

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Sale List",
        operation_description="Get Purchase Quotation Sale List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
