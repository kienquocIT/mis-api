from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.masterdata.saledata.models import GoodReceipt
from apps.masterdata.saledata.serializers import GoodReceiptListSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view

__all__ = ['GoodReceiptList']


class GoodReceiptList(
    BaseListMixin,
    BaseCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = GoodReceipt.objects
    search_fields = ["search_content"]

    serializer_list = GoodReceiptListSerializer
    serializer_create = GoodReceiptListSerializer
    serializer_detail = GoodReceiptListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
        )

    @swagger_auto_schema(
        operation_summary="Good receipt list",
        operation_description="Good receipt list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Good receipt",
        operation_description="Create new Good receipt",
        request_body=GoodReceiptListSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
