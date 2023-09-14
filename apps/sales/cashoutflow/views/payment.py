from drf_yasg.utils import swagger_auto_schema
from apps.sales.cashoutflow.models import Payment, PaymentCostItems, PaymentConfig
from apps.sales.cashoutflow.serializers import (
    PaymentListSerializer, PaymentCreateSerializer, PaymentDetailSerializer, PaymentCostItemsListSerializer,
    PaymentConfigListSerializer, PaymentConfigUpdateSerializer, PaymentConfigDetailSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class PaymentList(BaseListMixin, BaseCreateMixin):
    queryset = Payment.objects
    serializer_list = PaymentListSerializer
    serializer_create = PaymentCreateSerializer
    serializer_detail = PaymentDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment'
        )

    @swagger_auto_schema(
        operation_summary="Payment list",
        operation_description="Payment list",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Payment",
        operation_description="Create new Payment",
        request_body=PaymentCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Payment.objects  # noqa
    serializer_list = PaymentListSerializer
    serializer_create = PaymentCreateSerializer
    serializer_detail = PaymentDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment'
        )

    @swagger_auto_schema(operation_summary='Detail Payment')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # @swagger_auto_schema(operation_summary="Update AdvancePayment", request_body=PaymentUpdateSerializer)
    # @mask_view(login_require=True, auth_require=False)
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
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PaymentConfigList(BaseListMixin, BaseCreateMixin):
    queryset = PaymentConfig.objects
    serializer_list = PaymentConfigListSerializer
    serializer_create = PaymentConfigUpdateSerializer
    serializer_detail = PaymentConfigDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            'employee_allowed'
        )

    @swagger_auto_schema(
        operation_summary="Payment Config list",
        operation_description="Payment Config list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Payment Config",
        operation_description="Create new Payment Config",
        request_body=PaymentConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_current': request.user.company_current
        }
        return self.create(request, *args, **kwargs)
