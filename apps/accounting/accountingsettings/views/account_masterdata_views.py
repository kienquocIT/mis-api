from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models.account_masterdata_models import (
    ChartOfAccounts, DefaultAccountDetermination
)
from apps.accounting.accountingsettings.serializers.account_masterdata_serializers import (
    ChartOfAccountsListSerializer, ChartOfAccountsCreateSerializer, ChartOfAccountsDetailSerializer,
    DefaultAccountDeterminationListSerializer, DefaultAccountDeterminationCreateSerializer,
    DefaultAccountDeterminationDetailSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view


# Create your views here.
class ChartOfAccountsList(BaseListMixin, BaseCreateMixin):
    queryset = ChartOfAccounts.objects
    search_fields = ['acc_code', 'acc_name', 'foreign_acc_name']
    serializer_list = ChartOfAccountsListSerializer
    serializer_create = ChartOfAccountsCreateSerializer
    serializer_detail = ChartOfAccountsDetailSerializer
    filterset_fields = {'acc_type': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related('currency_mapped')

    @swagger_auto_schema(
        operation_summary="Chart Of Accounts list",
        operation_description="Chart Of Accounts list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Main Account",
        operation_description="Create new Main Account",
        request_body=ChartOfAccountsCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DefaultAccountDeterminationList(BaseListMixin, BaseCreateMixin):
    queryset = DefaultAccountDetermination.objects
    search_fields = ['title',]
    serializer_list = DefaultAccountDeterminationListSerializer
    serializer_create = DefaultAccountDeterminationCreateSerializer
    serializer_detail = DefaultAccountDeterminationDetailSerializer
    filterset_fields = {'default_account_determination_type': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Default Account Determination List",
        operation_description="Default Account Determination List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Default Account Determination",
        operation_description="Create new Default Account Determination",
        request_body=DefaultAccountDeterminationCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
