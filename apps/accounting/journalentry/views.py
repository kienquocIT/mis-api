from drf_yasg.utils import swagger_auto_schema

from apps.accounting.journalentry.models import JournalEntry
from apps.accounting.journalentry.serializers import (
    JournalEntryListSerializer, JournalEntryCreateSerializer, JournalEntryDetailSerializer, JournalEntryUpdateSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class JournalEntryList(BaseListMixin, BaseCreateMixin):
    queryset = JournalEntry.objects
    search_fields = ['title', 'code']
    serializer_list = JournalEntryListSerializer
    serializer_create = JournalEntryCreateSerializer
    serializer_detail = JournalEntryDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Journal Entry list",
        operation_description="Journal Entry list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Journal Entry",
        operation_description="Create new Journal Entry",
        request_body=JournalEntryCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class JournalEntryDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = JournalEntry.objects  # noqa
    serializer_detail = JournalEntryDetailSerializer
    serializer_update = JournalEntryUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'je_items'
        ).select_related()

    @swagger_auto_schema(operation_summary='Detail Journal Entry')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Journal Entry", request_body=JournalEntryUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
