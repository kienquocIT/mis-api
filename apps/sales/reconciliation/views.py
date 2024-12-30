from drf_yasg.utils import swagger_auto_schema
from apps.sales.reconciliation.models import Reconciliation
from apps.sales.reconciliation.serializers import (
    ReconListSerializer, ReconDetailSerializer, ReconCreateSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin


__all__ = [
    'ReconList',
    'ReconDetail',
]


class ReconList(BaseListMixin, BaseCreateMixin):
    queryset = Reconciliation.objects
    search_fields = ['title', 'customer__name']
    serializer_list = ReconListSerializer
    serializer_create = ReconCreateSerializer
    serializer_detail = ReconDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(
        operation_summary="Recon list",
        operation_description="Recon list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialrecon', model_code='reconciliation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Recon",
        operation_description="Create new Recon",
        request_body=ReconCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialrecon', model_code='reconciliation', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ReconDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Reconciliation.objects  # noqa
    serializer_list = ReconListSerializer
    serializer_create = ReconCreateSerializer
    serializer_detail = ReconDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related().prefetch_related()

    @swagger_auto_schema(operation_summary='Detail Recon')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='financialrecon', model_code='reconciliation', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
