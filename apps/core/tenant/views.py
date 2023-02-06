from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.tenant.models import TenantPlan
from apps.core.tenant.serializers import TenantPlanSerializer
from apps.shared import ResponseController


class TenantPlanList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TenantPlan.objects
    search_fields = []

    serializer_class = TenantPlanSerializer

    @swagger_auto_schema(
        operation_summary="Tenant Plan list",
        operation_description="Get tenant plan list",
    )
    def get(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            queryset = self.filter_queryset(
                self.get_queryset()
                .filter(**kwargs)
            )
            serializer = self.serializer_class(queryset, many=True)
            return ResponseController.success_200(serializer.data, key_data='result')
        return ResponseController.unauthorized_401()
