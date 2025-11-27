from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.accounting.journalentry.models import (
    JournalEntry, JournalEntryLine, JE_ALLOWED_APP,
    AllowedAppAutoJournalEntry,
)
from apps.accounting.journalentry.serializers import (
    JournalEntryListSerializer, JournalEntryCreateSerializer, JournalEntryDetailSerializer,
    JournalEntryUpdateSerializer, AllowedAppAutoJEListSerializer, AllowedAppAutoJEUpdateSerializer,
    JournalEntryLineListSerializer,
)
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin


class AllowedAppAutoJEList(BaseListMixin):
    queryset = AllowedAppAutoJournalEntry.objects
    search_fields = ['title', 'code']
    serializer_list = AllowedAppAutoJEListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Allowed App Auto Journal Entry List",
        operation_description="Allowed App Auto Journal Entry List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AllowedAppAutoJEDetail(BaseUpdateMixin):
    queryset = AllowedAppAutoJournalEntry.objects
    serializer_update = AllowedAppAutoJEUpdateSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update Allowed App Auto Journal Entr",
        request_body=AllowedAppAutoJEUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
    all_je = JournalEntry.objects.filter_on_company()

    summarize_total_je = all_je.count()
    summarize_total_debit = sum(all_je.values_list('total_debit', flat=True))
    summarize_total_credit = sum(all_je.values_list('total_credit', flat=True))

    summarize_total_source_type = len(JE_ALLOWED_APP)

    return Response(
        {
            'result': {
                'summarize_total_je': summarize_total_je,
                'summarize_total_debit': summarize_total_debit,
                'summarize_total_credit': summarize_total_credit,
                'summarize_total_source_type': summarize_total_source_type,
            }
        }
    )


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
        return self.list(request, *args, **kwargs)
