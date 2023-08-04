from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.purchasing.models import PurchaseRequest
from apps.sales.purchasing.serializers import (
    PurchaseRequestListSerializer, PurchaseRequestCreateSerializer, PurchaseRequestDetailSerializer,
    PurchaseRequestListForPQRSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class PurchaseRequestList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseRequest.objects

    serializer_list = PurchaseRequestListSerializer
    serializer_create = PurchaseRequestCreateSerializer
    serializer_detail = PurchaseRequestListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
            'sale_order',
        )

    @swagger_auto_schema(
        operation_summary="Purchase Request List",
        operation_description="Get Purchase Request List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Purchase Request",
        operation_description="Create new Purchase Request",
        request_body=PurchaseRequestCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PurchaseRequestDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseRequest.objects
    serializer_detail = PurchaseRequestDetailSerializer
    serializer_update = PurchaseRequestDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
            'sale_order',
            'contact'
        )

    @swagger_auto_schema(
        operation_summary="Purchase Request detail",
        operation_description="Get Purchase Request detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class PurchaseRequestListForPQR(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseRequest.objects

    serializer_list = PurchaseRequestListForPQRSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Purchase Request List For Purchase Quotation Request",
        operation_description="Get Purchase Request List For Purchase Quotation Request",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
