from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.shared import ResponseController
from apps.core.base.models import SubscriptionPlan

from apps.core.base.serializers import PlanListSerializer


# Subscription Plan
class PlanList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubscriptionPlan.objects
    search_fields = []

    serializer_class = PlanListSerializer

    @swagger_auto_schema(
        operation_summary="Plan list",
        operation_description="Get plan list",
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

