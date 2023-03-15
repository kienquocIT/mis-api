from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.core.tenant.models import TenantPlan
from apps.core.tenant.serializers import TenantPlanSerializer
from apps.shared import ResponseController, mask_view


class TenantPlanList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TenantPlan.objects
    search_fields = []

    serializer_class = TenantPlanSerializer

    @swagger_auto_schema(
        operation_summary="Tenant Plan list",
        operation_description="Get tenant plan list",
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(tenant_id=request.user.tenant_current_id)
        )
        serializer = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(serializer.data, key_data='result')
