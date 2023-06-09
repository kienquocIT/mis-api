from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.opportunity.models import OpportunityDecisionFactor
from apps.sales.opportunity.serializers import OpportunityDecisionFactorListSerializer, \
    OpportunityDecisionFactorCreateSerializer, OpportunityDecisionFactorDetailSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin


class OpportunityDecisionFactorList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityDecisionFactor.objects
    serializer_list = OpportunityDecisionFactorListSerializer
    serializer_create = OpportunityDecisionFactorCreateSerializer
    serializer_detail = OpportunityDecisionFactorListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Opportunity Customer Decision Factor List",
        operation_description="Get Opportunity Customer Decision Factor",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity Customer Decision Facto",
        operation_description="Create new Opportunity Customer Decision Factor",
        request_body=OpportunityDecisionFactorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
