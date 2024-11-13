from drf_yasg.utils import swagger_auto_schema

from apps.core.recurrence.models import Recurrence
from apps.core.recurrence.serializers import RecurrenceListSerializer, RecurrenceCreateSerializer, \
    RecurrenceDetailSerializer, RecurrenceUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class RecurrenceList(BaseListMixin, BaseCreateMixin):
    queryset = Recurrence.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'application_id': ['exact'],
    }
    serializer_list = RecurrenceListSerializer
    serializer_create = RecurrenceCreateSerializer
    serializer_detail = RecurrenceListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    @swagger_auto_schema(
        operation_summary="Recurrence List",
        operation_description="Get Recurrence List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='recurrence', model_code='recurrence', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Recurrence",
        operation_description="Create New Recurrence",
        request_body=RecurrenceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='recurrence', model_code='recurrence', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RecurrenceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Recurrence.objects
    serializer_detail = RecurrenceDetailSerializer
    serializer_update = RecurrenceUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Recurrence Detail",
        operation_description="Get Recurrence Detail By ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='recurrence', model_code='recurrence', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Recurrence",
        operation_description="Update Recurrence By ID",
        request_body=RecurrenceUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='recurrence', model_code='recurrence', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
