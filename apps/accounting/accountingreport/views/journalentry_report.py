from django_filters import rest_framework
from drf_yasg.utils import swagger_auto_schema

from apps.accounting.accountingreport.serializers.journalentry_report import JournalEntryLineListSerializer
from apps.accounting.journalentry.models import JournalEntryLine
from apps.shared import BaseListMixin, mask_view


class JournalEntryLineFilter(rest_framework.FilterSet):
    from_date = rest_framework.DateFilter(field_name='journal_entry__date_created', lookup_expr='date__gte')
    to_date = rest_framework.DateFilter(field_name='journal_entry__date_created', lookup_expr='date__lte')

    class Meta:
        model = JournalEntryLine
        fields = ['account_id']


class JournalEntryLineList(BaseListMixin):
    queryset = JournalEntryLine.objects
    serializer_list = JournalEntryLineListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_class = JournalEntryLineFilter

    def get_queryset(self):
        print(self.request.query_params)
        if 'is_general_ledger' in self.request.query_params and self.request.query_params.get('account_id') is None:
            return super().get_queryset().none()
        return super().get_queryset().filter(journal_entry__system_status=3).select_related(
            'journal_entry',
            'journal_entry__employee_created',
            'account',
            'product_mapped',
            'business_partner',
            'business_employee',
            'currency_mapped'
        ).order_by(
            '-journal_entry__date_created'
        )

    @swagger_auto_schema(
        operation_summary="Journal Entry Line List",
        operation_description="Get all Journal Entry Lines",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)
