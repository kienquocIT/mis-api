from drf_yasg.utils import swagger_auto_schema
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.lead.models import Lead
from apps.sales.lead.serializers import (
    LeadListSerializer, LeadCreateSerializer, LeadDetailSerializer, LeadUpdateSerializer
)

__all__ = [
    'LeadList',
    'LeadDetail'
]


class LeadList(BaseListMixin, BaseCreateMixin):
    queryset = Lead.objects
    search_fields = ['title']
    serializer_list = LeadListSerializer
    serializer_create = LeadCreateSerializer
    serializer_detail = LeadDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Lead list",
        operation_description="Lead list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Lead",
        operation_description="Create new Lead",
        request_body=LeadCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LeadDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Lead.objects  # noqa
    serializer_list = LeadListSerializer
    serializer_create = LeadCreateSerializer
    serializer_detail = LeadDetailSerializer
    serializer_update = LeadUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail Lead')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ARInvoice", request_body=LeadUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = LeadUpdateSerializer
        return self.update(request, *args, **kwargs)
