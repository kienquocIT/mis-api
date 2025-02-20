from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models import ChartOfAccounts, DefaultAccountDefinition
from apps.accounting.accountingsettings.serializers import (
    ChartOfAccountsListSerializer, ChartOfAccountsCreateSerializer, ChartOfAccountsDetailSerializer,
    DefaultAccountDefinitionListSerializer, DefaultAccountDefinitionCreateSerializer,
    DefaultAccountDefinitionDetailSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view


# Create your views here.
class ChartOfAccountsList(BaseListMixin, BaseCreateMixin):
    queryset = ChartOfAccounts.objects
    search_fields = ['title', 'code']
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


class DefaultAccountDefinitionList(BaseListMixin, BaseCreateMixin):
    queryset = DefaultAccountDefinition.objects
    search_fields = ['title',]
    serializer_list = DefaultAccountDefinitionListSerializer
    serializer_create = DefaultAccountDefinitionCreateSerializer
    serializer_detail = DefaultAccountDefinitionDetailSerializer
    filterset_fields = {'default_account_definition_type': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related('account_mapped')

    @swagger_auto_schema(
        operation_summary="Default Account Definition List",
        operation_description="Default Account Definition List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Default Account Definition",
        operation_description="Create new Default Account Definition",
        request_body=DefaultAccountDefinitionCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
