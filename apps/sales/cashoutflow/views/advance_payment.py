from drf_yasg.utils import swagger_auto_schema
from apps.sales.cashoutflow.models import AdvancePayment, AdvancePaymentCost
from apps.sales.cashoutflow.serializers import (
    AdvancePaymentListSerializer, AdvancePaymentCreateSerializer,
    AdvancePaymentDetailSerializer, AdvancePaymentUpdateSerializer,
    AdvancePaymentCostListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class AdvancePaymentList(BaseListMixin, BaseCreateMixin):
    queryset = AdvancePayment.objects
    serializer_list = AdvancePaymentListSerializer
    serializer_create = AdvancePaymentCreateSerializer
    serializer_detail = AdvancePaymentDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'advance_payment__currency',
            'advance_payment__expense_type',
            'advance_payment__expense_tax',
        ).select_related(
            'sale_order_mapped__opportunity',
            'quotation_mapped__opportunity',
            'opportunity_mapped',
        )

    @swagger_auto_schema(
        operation_summary="AdvancePayment list",
        operation_description="AdvancePayment list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='advancepayment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create AdvancePayment",
        operation_description="Create new AdvancePayment",
        request_body=AdvancePaymentCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='advancepayment', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AdvancePaymentDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = AdvancePayment.objects  # noqa
    serializer_list = AdvancePaymentListSerializer
    serializer_create = AdvancePaymentCreateSerializer
    serializer_detail = AdvancePaymentDetailSerializer
    serializer_update = AdvancePaymentUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'advance_payment__currency',
            'advance_payment__expense_type',
            'advance_payment__expense_tax',
        ).select_related(
            'sale_order_mapped__opportunity__customer',
            'sale_order_mapped__quotation__customer',
            'quotation_mapped__opportunity__customer',
            'opportunity_mapped__customer',
            'supplier__owner',
            'supplier__industry',
            'employee_inherit__group',
            'creator_name__group'
        )

    @swagger_auto_schema(operation_summary='Detail AdvancePayment')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='advancepayment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update AdvancePayment", request_body=AdvancePaymentUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='advancepayment', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = AdvancePaymentUpdateSerializer
        return self.update(request, *args, **kwargs)


class AdvancePaymentCostList(BaseListMixin):
    queryset = AdvancePaymentCost.objects
    filterset_fields = {
        'opportunity_mapped_id': ['exact'],
        'quotation_mapped_id': ['exact'],
        'sale_order_mapped_id': ['exact'],
    }
    serializer_list = AdvancePaymentCostListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related('expense_type', 'expense_tax')

    @swagger_auto_schema(
        operation_summary="AdvancePaymentCost List",
        operation_description="Get AdvancePaymentCost List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
