from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.sales.purchasing.models import PurchaseQuotationRequest
from apps.sales.purchasing.serializers import (
    PurchaseQuotationRequestListSerializer, PurchaseQuotationRequestDetailSerializer,
    PurchaseQuotationRequestCreateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseQuotationRequestList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseQuotationRequest.objects

    serializer_list = PurchaseQuotationRequestListSerializer
    serializer_create = PurchaseQuotationRequestCreateSerializer
    serializer_detail = PurchaseQuotationRequestDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'purchase_quotation_request', 'purchase_quotation_request_mapped'
        )

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Request List",
        operation_description="Get Purchase Quotation Request List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase Quotation Request",
        operation_description="Create new Purchase Quotation Request",
        request_body=PurchaseQuotationRequestCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PurchaseQuotationRequestDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseQuotationRequest.objects
    serializer_detail = PurchaseQuotationRequestDetailSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'purchase_quotation_request', 'purchase_quotation_request_mapped',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Quotation Request detail",
        operation_description="Get Purchase Quotation Request detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
