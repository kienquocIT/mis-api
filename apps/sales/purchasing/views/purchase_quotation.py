from drf_yasg.utils import swagger_auto_schema
from apps.sales.purchasing.models import PurchaseQuotation, PurchaseQuotationProduct
from apps.sales.purchasing.serializers import (
    PurchaseQuotationListSerializer, PurchaseQuotationDetailSerializer,
    PurchaseQuotationCreateSerializer, PurchaseQuotationProductListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseQuotationList(BaseListMixin, BaseCreateMixin):
    queryset = PurchaseQuotation.objects
    filterset_fields = {
        'purchase_quotation_request_mapped__purchase_request_mapped__id': ['in', 'exact'],
    }
    serializer_list = PurchaseQuotationListSerializer
    serializer_create = PurchaseQuotationCreateSerializer
    serializer_detail = PurchaseQuotationDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id', 'employee_modified_id']

    def get_queryset(self):
        # Check filter parameters in the request
        data_filter = self.request.query_params.dict()
        if 'purchase_quotation_request_mapped__purchase_request_mapped__id__in' in data_filter:
            return super().get_queryset().select_related(
                'purchase_quotation_request_mapped',
                'supplier_mapped'
            ).distinct()
        return super().get_queryset().select_related('purchase_quotation_request_mapped', 'supplier_mapped')

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
    update_hidden_field = ['employee_modified_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier_mapped',
            'contact_mapped',
            'purchase_quotation_request_mapped'
        ).prefetch_related(
            'purchase_quotation'
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


class PurchaseQuotationProductList(BaseListMixin):
    queryset = PurchaseQuotationProduct.objects
    filterset_fields = {
        'purchase_quotation_id': ['in', 'exact'],
    }
    serializer_list = PurchaseQuotationProductListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().select_related(
            'purchase_quotation'
        ).order_by('-purchase_quotation__date_created')

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Product List",
        operation_description="Get Purchase Quotation Product List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
