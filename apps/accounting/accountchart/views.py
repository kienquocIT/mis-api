from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountchart.models import AccountingAccount
from apps.accounting.accountchart.serializers import (
    AccountingAccountListSerializer, AccountingAccountCreateSerializer, AccountingAccountDetailSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view


# Create your views here.
class AccountingAccountList(BaseListMixin, BaseCreateMixin):
    queryset = AccountingAccount.objects
    search_fields = ['title', 'code']
    serializer_list = AccountingAccountListSerializer
    serializer_create = AccountingAccountCreateSerializer
    serializer_detail = AccountingAccountDetailSerializer
    filterset_fields = {'acc_type': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="Main Account list",
        operation_description="Main Account list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='cashoutflow', model_code='advancepayment', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Main Account",
        operation_description="Create new Main Account",
        request_body=AccountingAccountCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='cashoutflow', model_code='advancepayment', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)