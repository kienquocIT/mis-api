from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from apps.masterdata.saledata.models import GoodReceipt
from apps.masterdata.saledata.serializers import GoodReceiptListSerializer
from apps.masterdata.saledata.serializers.good_receipt import GoodReceiptCreateSerializer, \
    GoodReceiptDetailSerializer, GoodReceiptUpdateSerializer
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin

__all__ = ['GoodReceiptList', 'GoodReceiptDetail']


class GoodReceiptList(
    BaseListMixin,
    BaseCreateMixin,
    generics.GenericAPIView
):
    queryset = GoodReceipt.objects
    search_fields = ["search_content"]

    serializer_list = GoodReceiptListSerializer
    serializer_create = GoodReceiptCreateSerializer
    serializer_detail = GoodReceiptDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
        )

    @swagger_auto_schema(
        operation_summary="Good receipt list",
        operation_description="List of Good receipt",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Good receipt create",
        operation_description="Create new Good receipt",
        request_body=GoodReceiptCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.create(request, *args, **kwargs)


class GoodReceiptDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
    BaseDestroyMixin
):
    queryset = GoodReceipt.objects
    serializer_detail = GoodReceiptDetailSerializer
    serializer_update = GoodReceiptUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'supplier',
        )

    @swagger_auto_schema(operation_summary='Detail a good receipt')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(operation_summary='Update a good receipt', request_body=GoodReceiptUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.update(request, *args, pk, **kwargs)
