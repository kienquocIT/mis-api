from drf_yasg.utils import swagger_auto_schema
from apps.sales.financialcashflow.models import CashInflow
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.serializers import (
    ARInvoiceListForCashInflowSerializer, CashInflowListSerializer, CashInflowCreateSerializer,
    CashInflowDetailSerializer, CashInflowUpdateSerializer
)

__all__ = [
    'CashInflowList',
    'CashInflowDetail',
    'ARInvoiceListForCashInflow',
]


# main views
class CashInflowList(BaseListMixin, BaseCreateMixin):
    queryset = CashInflow.objects
    search_fields = ['title', 'code']
    serializer_list = CashInflowListSerializer
    serializer_create = CashInflowCreateSerializer
    serializer_detail = CashInflowDetailSerializer
    filterset_fields = {}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="CashInflow list",
        operation_description="CashInflow list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashinflow', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Cash Inflow",
        operation_description="Create new Cash Inflow",
        request_body=CashInflowCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashinflow', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CashInflowDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = CashInflow.objects
    serializer_detail = CashInflowDetailSerializer
    serializer_update = CashInflowUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail CashInflow')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashinflow', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update CashInflow", request_body=CashInflowUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialcashflow', model_code='cashinflow', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# related views
class ARInvoiceListForCashInflow(BaseListMixin):
    queryset = ARInvoice.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {'customer_mapped_id': ['exact']}
    serializer_list = ARInvoiceListForCashInflowSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related(
            'customer_mapped',
        ).order_by('date_created')

    @swagger_auto_schema(
        operation_summary="ARInvoice list",
        operation_description="ARInvoice list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
