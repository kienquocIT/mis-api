from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.accounting.accountingsettings.models.chart_of_account import (
    ChartOfAccounts, ChartOfAccountsSummarize, CHART_OF_ACCOUNT_TYPE
)
from apps.accounting.accountingsettings.serializers.chart_of_account import (
    ChartOfAccountsListSerializer, ChartOfAccountsCreateSerializer, ChartOfAccountsDetailSerializer,
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view


class ChartOfAccountsList(BaseListMixin, BaseCreateMixin):
    queryset = ChartOfAccounts.objects
    search_fields = ['acc_code', 'acc_name', 'foreign_acc_name']
    serializer_list = ChartOfAccountsListSerializer
    serializer_create = ChartOfAccountsCreateSerializer
    serializer_detail = ChartOfAccountsDetailSerializer
    filterset_fields = {
        'acc_type': ['exact'],
        'is_account': ['exact'],
    }
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().filter(
            acc_status=True
        ).prefetch_related().select_related('currency_mapped')

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


@swagger_auto_schema(
    method='get',
    operation_summary="Chart of Accounts Summarize",
    operation_description="Chart of Accounts Summarize",
)
@api_view(['GET'])
def get_chart_of_accounts_summarize(request, *args, **kwargs):
    account_id = request.query_params.get('account_id')
    account_level = request.query_params.get('account_level')
    account_display = request.query_params.get('account_display')

    filter_set = {
        'company_id': request.user.company_current_id,
    }
    exclude_set = {}

    if account_id:
        filter_set['account_id'] = account_id

    if account_level and int(account_level) >= 0:
        filter_set['account__level'] = account_level

    if account_display and int(account_display) == 1:
        exclude_set['closing_debit'] = 0
        exclude_set['closing_credit'] = 0

    queryset = ChartOfAccountsSummarize.objects.filter(
        **filter_set
    ).exclude(
        **exclude_set
    ).select_related('account').order_by(
        'account__acc_type',
        'account__acc_code'
    )

    data = []
    account_dict = dict(CHART_OF_ACCOUNT_TYPE)
    for obj in queryset:
        data.append({
            'account_id': obj.account_id,
            'account_code': obj.account.acc_code,
            'account_name': obj.account.acc_name,
            'foreign_account_name': obj.account.foreign_acc_name,
            'account_type_name': account_dict.get(obj.account.acc_type),
            'account_level': obj.account.level,
            'opening_debit': obj.opening_debit,
            'opening_credit': obj.opening_credit,
            'total_debit': obj.total_debit,
            'total_credit': obj.total_credit,
            'closing_debit': obj.closing_debit,
            'closing_credit': obj.closing_credit,
        })

    return Response({
        'result': data
    })
