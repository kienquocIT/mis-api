from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models import InitialBalance
from apps.accounting.accountingsettings.serializers import (
    InitialBalanceListSerializer, InitialBalanceDetailSerializer, InitialBalanceCreateSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, mask_view


class InitialBalanceList(BaseListMixin, BaseCreateMixin):
    queryset = InitialBalance.objects
    search_fields = ['title', 'code']
    serializer_list = InitialBalanceListSerializer
    serializer_create = InitialBalanceCreateSerializer
    serializer_detail = InitialBalanceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Initial Balance List",
        operation_description="Initial Balance List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Initial Balance",
        operation_description="Create Initial Balance",
        request_body=InitialBalanceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InitialBalanceDetail(BaseRetrieveMixin):
    queryset = InitialBalance.objects
    serializer_detail = InitialBalanceDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related('ib_line_initial_balance')

    @swagger_auto_schema(
        operation_summary="Initial Balance Detail",
        operation_description="Get Initial Balance Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
