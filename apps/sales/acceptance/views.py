from drf_yasg.utils import swagger_auto_schema

from apps.sales.acceptance.models import FinalAcceptance
from apps.sales.acceptance.serializers.final_acceptance import FinalAcceptanceListSerializer
from apps.shared import mask_view, BaseListMixin


# FINAL ACCEPTANCE
class FinalAcceptanceList(BaseListMixin):
    queryset = FinalAcceptance.objects
    search_fields = ['sale_order__title']
    filterset_fields = {
        'sale_order_id': ['exact'],
    }
    serializer_list = FinalAcceptanceListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "fa_indicator_final_acceptance",
        )

    @swagger_auto_schema(
        operation_summary="Final Acceptance List",
        operation_description="Get final acceptance List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='acceptance', model_code='finalacceptance', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
