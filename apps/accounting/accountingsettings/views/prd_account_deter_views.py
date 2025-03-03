from drf_yasg.utils import swagger_auto_schema
from apps.accounting.accountingsettings.models.prd_account_deter import ProductAccountDetermination
from apps.accounting.accountingsettings.serializers.prd_account_deter_serializers import (
    ProductAccountDeterminationListSerializer
)
from apps.shared import BaseListMixin, mask_view


# Create your views here.
class ProductAccountDeterminationList(BaseListMixin):
    queryset = ProductAccountDetermination.objects
    search_fields = ['title',]
    serializer_list = ProductAccountDeterminationListSerializer
    filterset_fields = {'product_mapped_id': ['exact']}
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Product Account Determination List",
        operation_description="Product Account Determination List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
