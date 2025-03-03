from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models.wh_account_deter import WarehouseAccountDetermination
from apps.accounting.accountingsettings.serializers.wh_account_deter_serializers import (
    WarehouseAccountDeterminationListSerializer
)
from apps.shared import BaseListMixin, mask_view


# Create your views here.
class WarehouseAccountDeterminationList(BaseListMixin):
    queryset = WarehouseAccountDetermination.objects
    search_fields = ['title',]
    serializer_list = WarehouseAccountDeterminationListSerializer
    filterset_fields = {'warehouse_mapped_id': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Warehouse Account Determination List",
        operation_description="Warehouse Account Determination List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
