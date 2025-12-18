from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.accounting.journalentry.models import JournalEntry, JournalEntrySummarize
from apps.accounting.journalentry.serializers import (
    JournalEntryListSerializer, JournalEntryCreateSerializer,
    JournalEntryDetailSerializer, JournalEntryUpdateSerializer
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class JournalEntryList(BaseListMixin, BaseCreateMixin):
    queryset = JournalEntry.objects
    search_fields = ['title', 'code', 'je_transaction_data__code']
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
            'je_lines'
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


@swagger_auto_schema(
    method='get',
    operation_summary="Journal Entry Summarize",
    operation_description="Journal Entry Summarize",
)
@api_view(['GET'])
def get_je_summarize(request, *args, **kwargs):
    je_summarize_obj = JournalEntrySummarize.objects.filter(company_id=request.user.company_current_id).first()

    return Response({
        'result': {
            'total_je_doc': je_summarize_obj.total_je_doc,
            'total_debit': je_summarize_obj.total_debit,
            'total_credit': je_summarize_obj.total_credit,
            'total_source_type': je_summarize_obj.total_source_type,
        } if je_summarize_obj else {}
    })
