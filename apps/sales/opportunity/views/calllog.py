from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.sales.opportunity.models import OpportunityCallLog
from apps.sales.opportunity.serializers import (
    OpportunityCallLogListSerializer, OpportunityCallLogCreateSerializer,
    OpportunityCallLogDetailSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class OpportunityCallLogList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityCallLog.objects

    serializer_list = OpportunityCallLogListSerializer
    serializer_create = OpportunityCallLogCreateSerializer
    serializer_detail = OpportunityCallLogDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity", "customer", "contact")

    @swagger_auto_schema(
        operation_summary="OpportunityCallLog List",
        operation_description="Get OpportunityCallLog List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Opportunity",
        operation_description="Create new Opportunity",
        request_body=OpportunityCallLogCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityCallLogDetail(BaseRetrieveMixin, BaseUpdateMixin,):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityCallLog.objects
    serializer_detail = OpportunityCallLogDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity", "customer", "contact")

    @swagger_auto_schema(
        operation_summary="OpportunityCallLog detail",
        operation_description="Get OpportunityCallLog detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
