from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.acceptance.models import FinalAcceptance, FinalAcceptanceIndicator
from apps.sales.acceptance.serializers.final_acceptance import FinalAcceptanceListSerializer, \
    FinalAcceptanceUpdateSerializer
from apps.shared import mask_view, BaseListMixin, BaseUpdateMixin, BaseRetrieveMixin


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
            Prefetch(
                "fa_indicator_final_acceptance",
                queryset=FinalAcceptanceIndicator.objects.select_related(
                    "sale_order_indicator",
                    'indicator',
                    'sale_order',
                    "payment",
                    "expense_item",
                    "labor_item",
                    "delivery_sub",
                )
            ),
        )

    @swagger_auto_schema(
        operation_summary="Final Acceptance List",
        operation_description="Get final acceptance List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='acceptance', model_code='finalacceptance', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class FinalAcceptanceDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    queryset = FinalAcceptance.objects
    serializer_detail = FinalAcceptanceListSerializer
    serializer_update = FinalAcceptanceUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Final Acceptance detail",
        operation_description="Get Final Acceptance detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='acceptance', model_code='finalacceptance', perm_code='view',
        opp_enabled=True, prj_enabled=True,
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Final Acceptance",
        operation_description="Update Final Acceptance by ID",
        request_body=FinalAcceptanceUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='acceptance', model_code='finalacceptance', perm_code='edit',
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
