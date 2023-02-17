from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.base.mixins import ApplicationListMixin
from apps.shared import ResponseController, BaseListMixin
from apps.core.base.models import SubscriptionPlan, Application, ApplicationProperty

from apps.core.base.serializers import PlanListSerializer, ApplicationListSerializer, ApplicationPropertyListSerializer


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


class TenantApplicationList(
    ApplicationListMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()

    serializer_list = ApplicationListSerializer
    list_hidden_field = []

    @swagger_auto_schema(
        operation_summary="Tenant Application list",
        operation_description="Get tenant application list",
    )
    def get(self, request, *args, **kwargs):
        return self.tenant_application_list(request, *args, **kwargs)


class ApplicationPropertyList(
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = ApplicationProperty.objects
    search_fields = []

    serializer_class = ApplicationPropertyListSerializer

    @swagger_auto_schema(
        operation_summary="Application Property list",
        operation_description="Get application property list",
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