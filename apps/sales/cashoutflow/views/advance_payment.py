from drf_yasg.utils import swagger_auto_schema
from apps.sales.cashoutflow.models import AdvancePayment
from apps.sales.cashoutflow.serializers import (
    AdvancePaymentListSerializer, AdvancePaymentCreateSerializer, AdvancePaymentDetailSerializer,
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class AdvancePaymentList(BaseListMixin, BaseCreateMixin):
    queryset = AdvancePayment.objects
    serializer_list = AdvancePaymentListSerializer
    serializer_create = AdvancePaymentCreateSerializer
    serializer_detail = AdvancePaymentDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="AdvancePayment list",
        operation_description="AdvancePayment list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create AdvancePayment",
        operation_description="Create new AdvancePayment",
        request_body=AdvancePaymentCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdvancePaymentDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AdvancePayment.objects  # noqa
    serializer_list = AdvancePaymentListSerializer
    serializer_create = AdvancePaymentCreateSerializer
    serializer_detail = AdvancePaymentDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'sale_order_mapped',
            'sale_order_mapped__opportunity',
            'quotation_mapped',
            'quotation_mapped__opportunity',
            'beneficiary',
        )

    @swagger_auto_schema(operation_summary='Detail AdvancePayment')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # @swagger_auto_schema(operation_summary="Update AdvancePayment", request_body=AdvancePaymentUpdateSerializer)
    # @mask_view(login_require=True, auth_require=True, code_perm='')
    # def put(self, request, *args, **kwargs):
    #     self.serializer_class = AdvancePaymentUpdateSerializer
    #     return self.update(request, *args, **kwargs)
