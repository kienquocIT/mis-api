from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.sales.opportunity.models import CustomerDecisionFactor, OpportunityConfig, OpportunityConfigStage
from apps.sales.opportunity.serializers import CustomerDecisionFactorListSerializer, \
    CustomerDecisionFactorCreateSerializer, CustomerDecisionFactorDetailSerializer, OpportunityConfigDetailSerializer, \
    OpportunityConfigUpdateSerializer, OpportunityConfigStageListSerializer, OpportunityConfigStageCreateSerializer, \
    OpportunityConfigStageDetailSerializer, OpportunityConfigStageUpdateSerializer
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin


class OpportunityConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = OpportunityConfig.objects  # noqa
    serializer_detail = OpportunityConfigDetailSerializer
    serializer_update = OpportunityConfigUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Opportunity Config Detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.lookup_field = 'company_id'
        self.kwargs['company_id'] = request.user.company_current_id
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Opportunity Config Update",
        request_body=OpportunityConfigUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
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
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity Customer Decision Factor",
        operation_description="Create new Opportunity Customer Decision Factor",
        request_body=CustomerDecisionFactorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomerDecisionFactorDetail(
    BaseDestroyMixin,
):
    queryset = CustomerDecisionFactor.objects

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Customer Decision Factor",
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OpportunityConfigStageList(
    BaseListMixin,
    BaseCreateMixin
):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityConfigStage.objects
    serializer_list = OpportunityConfigStageListSerializer
    serializer_create = OpportunityConfigStageCreateSerializer
    serializer_detail = OpportunityConfigStageDetailSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "company",
        ).prefetch_related(
            "stage_condition__condition_property",
        )

    @swagger_auto_schema(
        operation_summary="Opportunity Config Stage List",
        operation_description="Get Opportunity Config Stage",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity Customer Decision Factor",
        operation_description="Create new Opportunity Customer Decision Factor",
        request_body=CustomerDecisionFactorCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityConfigStageDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
    BaseDestroyMixin,
):
    queryset = OpportunityConfigStage.objects
    serializer_detail = OpportunityConfigStageDetailSerializer
    serializer_update = OpportunityConfigStageUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Opportunity Config Stage Detail",
    )
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Opportunity Config Stage Update",
        request_body=OpportunityConfigStageUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Config Stage",
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
