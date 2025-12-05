from drf_yasg.utils import swagger_auto_schema

from apps.accounting.accountingreport.serializers.journalentry_report import JournalEntryLineListSerializer
from apps.accounting.journalentry.models import JournalEntryLine
from apps.shared import BaseListMixin, mask_view


class JournalEntryLineList(BaseListMixin):
    queryset = JournalEntryLine.objects
    serializer_list = JournalEntryLineListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    filterset_fields = {
        'journal_entry__date_created': ['lte', 'gte'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related(
            'journal_entry',
            'account',
            'product_mapped',
            'business_partner',
            'business_employee',
            'currency_mapped'
        ).order_by(
            'journal_entry__date_created',
            'journal_entry__id',
            'je_line_type',
            'order'
        )

    @swagger_auto_schema(
        operation_summary="Journal Entry Line List",
        operation_description="Get all Journal Entry Lines",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        # self.pagination_class.page_size = -1
        return self.list(request, *args, **kwargs)
