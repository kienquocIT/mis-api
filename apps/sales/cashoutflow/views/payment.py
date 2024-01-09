from drf_yasg.utils import swagger_auto_schema
from apps.sales.cashoutflow.models import Payment, PaymentConfig, PaymentCost
from apps.sales.cashoutflow.serializers import (
    PaymentListSerializer, PaymentCreateSerializer, PaymentDetailSerializer, PaymentCostListSerializer,
    PaymentConfigListSerializer, PaymentConfigUpdateSerializer, PaymentConfigDetailSerializer,
    PaymentUpdateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class PaymentList(BaseListMixin, BaseCreateMixin):
    queryset = Payment.objects
    serializer_list = PaymentListSerializer
    serializer_create = PaymentCreateSerializer
    serializer_detail = PaymentDetailSerializer
    filterset_fields = {
        'opportunity_mapped_id': ['exact'],
    }
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment'
        ).select_related(
            'sale_order_mapped__opportunity',
            'quotation_mapped__opportunity',
            'opportunity_mapped',
        )

    @swagger_auto_schema(
        operation_summary="Payment list",
        operation_description="Payment list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='payment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Payment",
        operation_description="Create new Payment",
        request_body=PaymentCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='payment', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Payment.objects  # noqa
    serializer_list = PaymentListSerializer
    serializer_create = PaymentCreateSerializer
    serializer_detail = PaymentDetailSerializer
    serializer_update = PaymentUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'payment__currency',
            'payment__expense_type',
            'payment__expense_tax',
        ).select_related(
            'sale_order_mapped__customer',
            'quotation_mapped__customer',
            'opportunity_mapped__customer',
            'supplier__owner',
            'supplier__industry',
            'employee_inherit__group',
            'creator_name__group'
        )

    @swagger_auto_schema(operation_summary='Detail Payment')
    @mask_view(
        login_require=True, auth_require=False,
        label_code='cashoutflow', model_code='payment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Payment", request_body=PaymentUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='payment', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = PaymentUpdateSerializer
        return self.update(request, *args, **kwargs)


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
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_current': request.user.company_current
        }
        return self.create(request, *args, **kwargs)


class PaymentCostList(BaseListMixin):
    queryset = PaymentCost.objects
    filterset_fields = {
        'opportunity_mapped_id': ['exact'],
        'quotation_mapped_id': ['exact'],
        'sale_order_mapped_id': ['exact'],
        # 'payment__system_status': ['exact']
    }
    serializer_list = PaymentCostListSerializer

    def get_queryset(self):
        return super().get_queryset().filter(payment__system_status=3).select_related('expense_type')

    @swagger_auto_schema(
        operation_summary="PaymentCost List",
        operation_description="Get PaymentCost List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
