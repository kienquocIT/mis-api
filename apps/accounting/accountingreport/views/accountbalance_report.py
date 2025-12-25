from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.accounting.accountingreport.serializers.accountbalance_report import ChartOfAccountTreeNodeSerializer
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.accountingsettings.models.chart_of_account import CHART_OF_ACCOUNT_TYPE
from apps.shared import mask_view, BaseListMixin


@swagger_auto_schema(
    method='get',
    operation_summary="Account Type Group",
    operation_description="Account Type Group",
)
@api_view(['GET'])
def get_account_type_group(request, *args, **kwargs):
    result = []
    for acc_type_value, acc_type_name in CHART_OF_ACCOUNT_TYPE:
        result.append({
            'acc_type': acc_type_value,
            'acc_type_name': str(acc_type_name),
        })
    return Response({'result': result})


class ChartOfAccountTypeTreeList(BaseListMixin):
    queryset = ChartOfAccounts.objects
    serializer_list = ChartOfAccountTreeNodeSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    filterset_fields = {
        'acc_type': ['in'],
        'level': ['in']
    }

    @swagger_auto_schema(
        operation_summary="Chart Of Account Type Tree",
        operation_description="Chart Of Account Type Tree",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
