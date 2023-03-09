from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.shared import ResponseController, mask_view

from .models import SubscriptionPlan, PermissionApplication, Application
from .serializers import PlanListSerializer, PermissionApplicationListSerializer, ApplicationListSerializer


class PlanList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubscriptionPlan.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "id": ["in"],
        "code": ["exact", "in"],
    }

    serializer_class = PlanListSerializer

    @swagger_auto_schema(
        operation_summary="Plan list",
        operation_description="Get plan list",
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter())
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')


class ApplicationList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Application.objects
    search_fields = ('title', 'code',)
    serializer_class = ApplicationListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter())
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')


class PermissionApplicationList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PermissionApplication.objects
    search_fields = ('permission', 'app__title', 'app__code',)
    filterset_fields = {
        'app_id': ['exact', 'in'],
        'app__code': ['exact', 'in'],
    }
    serializer_class = PermissionApplicationListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("app")

    @swagger_auto_schema(
        operation_summary="Plan list",
        operation_description="Get plan list",
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter())
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')
