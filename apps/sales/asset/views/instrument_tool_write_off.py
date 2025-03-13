from drf_yasg.utils import swagger_auto_schema

from apps.sales.asset.models import  InstrumentToolWriteOff
from apps.sales.asset.serializers import InstrumentToolWriteOffListSerializer,InstrumentToolWriteOffCreateSerializer, \
    InstrumentToolWriteOffDetailSerializer, InstrumentToolWriteOffUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin

__all__ =[
    'InstrumentToolWriteOffList',
    'InstrumentToolWriteOffDetail'
]

class InstrumentToolWriteOffList(BaseListMixin, BaseCreateMixin):
    queryset = InstrumentToolWriteOff.objects
    search_fields = ['title', 'code']
    filterset_fields = {}
    serializer_list = InstrumentToolWriteOffListSerializer
    serializer_create = InstrumentToolWriteOffCreateSerializer
    serializer_detail = InstrumentToolWriteOffDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related('quantities')

    @swagger_auto_schema(
        operation_summary="Instrument Tool Writeoff List",
        operation_description="Get Instrument Tool Writeoff List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttoolwriteoff', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Instrument Tool Writeoff",
        operation_description="Create New Instrument Tool Writeoff",
        request_body=InstrumentToolWriteOffCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        employee_require=True,
        label_code='asset', model_code='instrumenttoolwriteoff', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {'user': request.user}
        return self.create(request, *args, **kwargs)


class InstrumentToolWriteOffDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = InstrumentToolWriteOff.objects
    serializer_detail = InstrumentToolWriteOffDetailSerializer
    serializer_update = InstrumentToolWriteOffUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Instrument Tool Writeoff Detail",
        operation_description="Get Instrument Tool Writeoff Detail",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttoolwriteoff', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Instrument Tool Writeoff Update",
        operation_description="Instrument Tool Writeoff Update",
        request_body=InstrumentToolWriteOffUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='asset', model_code='instrumenttoolwriteoff', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        self.ser_context = {
            'instrument_tool_write_off_id': pk,
            'user': request.user
        }
        return self.update(request, *args, pk, **kwargs)
