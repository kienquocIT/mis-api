from drf_yasg.utils import swagger_auto_schema

from apps.accounting.accountingreport.serializers.journalentry_report import JournalEntryLineListSerializer
from apps.accounting.journalentry.models import JournalEntryLine
from apps.shared import BaseListMixin, mask_view


class JournalEntryLineList(BaseListMixin):
    queryset = JournalEntryLine.objects
    serializer_list = JournalEntryLineListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

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
