from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.opportunity.models import Opportunity
from apps.sales.opportunity.serializers import OpportunityListSerializer, OpportunityUpdateSerializer, \
    OpportunityCreateSerializer, OpportunityDetailSerializer, OpportunityForSaleListSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class OpportunityList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = Opportunity.objects
    filterset_fields = {
        'sale_person_id': ['exact'],
        'quotation': ['exact', 'isnull'],
        'sale_order': ['exact', 'isnull'],
        'is_close_lost': ['exact'],
        'is_deal_close': ['exact'],
        'id': ['in'],
    }
    serializer_list = OpportunityListSerializer
    serializer_create = OpportunityCreateSerializer
    serializer_detail = OpportunityListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person",
        ).prefetch_related(
            "opportunity_stage_opportunity__stage",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity List",
        operation_description="Get Opportunity List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity",
        operation_description="Create new Opportunity",
        request_body=OpportunityCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Opportunity.objects
    serializer_detail = OpportunityDetailSerializer
    serializer_update = OpportunityUpdateSerializer
    update_hidden_field = ['tenant_id', 'company_id']
    retrieve_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "decision_maker",
            "sale_person",
            "sale_order__delivery_of_sale_order",
            "quotation",

        ).prefetch_related(
            "stage",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity detail",
        operation_description="Get Opportunity detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Opportunity",
        operation_description="Update Opportunity by ID",
        request_body=OpportunityUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Opportunity List use for Sale Apps
class OpportunityForSaleList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Opportunity.objects
    filterset_fields = {
        'sale_person_id': ['exact'],
        'quotation': ['exact', 'isnull'],
        'sale_order': ['exact', 'isnull'],
        'is_close_lost': ['exact'],
        'is_deal_close': ['exact'],
        'id': ['in'],
    }
    serializer_list = OpportunityForSaleListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
            "sale_person",
            'customer__industry',
            'customer__owner',
            'customer__payment_term_mapped',
            'customer__price_list_mapped'
        ).prefetch_related(
            "opportunity_stage_opportunity__stage",
            "customer__account_mapped_shipping_address",
            "customer__account_mapped_billing_address",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity List For Sales",
        operation_description="Get Opportunity List For Sales",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
