from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.opportunity.models import Opportunity
from apps.sales.opportunity.serializers import OpportunityListSerializer, OpportunityUpdateSerializer, \
    OpportunityCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class OpportunityList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = Opportunity.objects
    filterset_fields = []
    serializer_list = OpportunityListSerializer
    serializer_create = OpportunityCreateSerializer
    serializer_detail = OpportunityListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity List",
        operation_description="Get Opportunity List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity",
        operation_description="Create new Opportunity",
        request_body=OpportunityCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Opportunity.objects
    serializer_detail = OpportunityListSerializer
    serializer_update = OpportunityUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            "customer",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity detail",
        operation_description="Get Opportunity detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.serializer_class = OpportunityListSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Opportunity",
        operation_description="Update Opportunity by ID",
        request_body=OpportunityUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = OpportunityUpdateSerializer
        return self.update(request, *args, **kwargs)
