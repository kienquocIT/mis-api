from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.opportunity.models import CustomerDecisionFactor, OpportunityConfig
from apps.sales.opportunity.serializers import CustomerDecisionFactorListSerializer, \
    CustomerDecisionFactorCreateSerializer, CustomerDecisionFactorDetailSerializer, OpportunityConfigDetailSerializer, \
    OpportunityConfigUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin


class OpportunityConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = OpportunityConfig.objects  # noqa
    serializer_detail = OpportunityConfigDetailSerializer
    serializer_update = OpportunityConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Opportunity Config Detail",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Opportunity Config Update",
        request_body=OpportunityConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.update(request, *args, **kwargs)


class CustomerDecisionFactorList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = CustomerDecisionFactor.objects
    serializer_list = CustomerDecisionFactorListSerializer
    serializer_create = CustomerDecisionFactorCreateSerializer
    serializer_detail = CustomerDecisionFactorDetailSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "company"
        )

    @swagger_auto_schema(
        operation_summary="Opportunity Customer Decision Factor List",
        operation_description="Get Opportunity Customer Decision Factor",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity Customer Decision Factor",
        operation_description="Create new Opportunity Customer Decision Factor",
        request_body=CustomerDecisionFactorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomerDecisionFactorDetail(
    BaseDestroyMixin,
):

    queryset = CustomerDecisionFactor.objects
    @swagger_auto_schema(
        operation_summary="Delete Opportunity Customer Decision Factor",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
