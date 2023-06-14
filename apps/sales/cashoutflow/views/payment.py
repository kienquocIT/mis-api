from drf_yasg.utils import swagger_auto_schema
from apps.sales.cashoutflow.models import Payment, PaymentCostItems
from apps.sales.cashoutflow.serializers import (
    PaymentListSerializer, PaymentCreateSerializer,
    PaymentDetailSerializer,
    PaymentCostItemsListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class PaymentList(BaseListMixin, BaseCreateMixin):
    queryset = Payment.objects
    serializer_list = PaymentListSerializer
    serializer_create = PaymentCreateSerializer
    serializer_detail = PaymentDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment'
        )

    @swagger_auto_schema(
        operation_summary="Payment list",
        operation_description="Payment list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Payment",
        operation_description="Create new Payment",
        request_body=PaymentCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Payment.objects  # noqa
    serializer_list = PaymentListSerializer
    serializer_create = PaymentCreateSerializer
    serializer_detail = PaymentDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment'
        )

    @swagger_auto_schema(operation_summary='Detail Payment')
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # @swagger_auto_schema(operation_summary="Update AdvancePayment", request_body=PaymentUpdateSerializer)
    # @mask_view(login_require=True, auth_require=True, code_perm='')
    # def put(self, request, *args, **kwargs):
    #     self.serializer_class = PaymentUpdateSerializer
    #     return self.update(request, *args, **kwargs)


class PaymentCostItemsList(BaseListMixin):
    queryset = PaymentCostItems.objects
    serializer_list = PaymentCostItemsListSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment_cost'
        )

    @swagger_auto_schema(
        operation_summary="Payment Cost Items list",
        operation_description="Payment Cost Items list",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        kwargs.update(
            {
                'sale_code_mapped': request.query_params['filter_sale_code'],
            }
        )
        return self.list(request, *args, **kwargs)
