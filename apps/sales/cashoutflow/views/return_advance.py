from drf_yasg.utils import swagger_auto_schema
from apps.sales.cashoutflow.models import ReturnAdvance
from apps.sales.cashoutflow.serializers.return_advance import (
    ReturnAdvanceCreateSerializer, ReturnAdvanceListSerializer,
    ReturnAdvanceDetailSerializer, ReturnAdvanceUpdateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class ReturnAdvanceList(BaseListMixin, BaseCreateMixin):
    queryset = ReturnAdvance.objects
    search_fields = ['title']
    serializer_list = ReturnAdvanceListSerializer
    serializer_create = ReturnAdvanceCreateSerializer
    serializer_detail = ReturnAdvanceDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id',
        'company_id',
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'advance_payment'
        ).prefetch_related(
            'return_advance'
        )

    @swagger_auto_schema(
        operation_summary="Return Advance list",
        operation_description="Return Advance list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='returnadvance', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Return Advance",
        operation_description="Create new Return Advance",
        request_body=ReturnAdvanceCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='returnadvance', perm_code="create",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ReturnAdvanceDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = ReturnAdvance.objects # noqa
    serializer_detail = ReturnAdvanceDetailSerializer
    serializer_update = ReturnAdvanceUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'advance_payment', 'employee_inherit'
        )

    @swagger_auto_schema(operation_summary='Detail Return Advance')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='returnadvance', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Return Advance", request_body=ReturnAdvanceUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='cashoutflow', model_code='returnadvance', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
