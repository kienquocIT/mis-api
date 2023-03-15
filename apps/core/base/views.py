from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.core.base.mixins import ApplicationListMixin
from apps.shared import ResponseController, BaseListMixin, mask_view
from apps.core.base.models import SubscriptionPlan, Application, ApplicationProperty, PermissionApplication

from apps.core.base.serializers import (
    PlanListSerializer, ApplicationListSerializer, ApplicationPropertyListSerializer,
    PermissionApplicationListSerializer,
)


class PlanList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubscriptionPlan.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "id": ["in"],
        "code": ["exact", "in"],
    }

    serializer_class = PlanListSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('applications')

    @swagger_auto_schema(
        operation_summary="Plan list",
        operation_description="Get plan list",
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter()).cache(timeout=60 * 60 * 1)  # cache 1 days
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')


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
    BaseListMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = ApplicationProperty.objects
    search_fields = []
    filterset_fields = ['application', 'type']
    serializer_list = ApplicationPropertyListSerializer

    @swagger_auto_schema(
        operation_summary="Application Property list",
        operation_description="Get application property list",
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        code_perm=''
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationPropertyEmployeeList(
    BaseListMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = ApplicationProperty.objects
    serializer_list = ApplicationPropertyListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().filter(
            content_type="hr_employee"
        )

    @swagger_auto_schema(
        operation_summary="Property list have employee data",
        operation_description="Property list have employee data",
    )
    @mask_view(
        login_require=True,
        auth_require=True,
        code_perm=''
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationList(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Application.objects
    search_fields = ('title', 'code',)
    serializer_class = ApplicationListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter()).cache(timeout=60 * 60 * 1)  # cache 1 days
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
        queryset = self.filter_queryset(self.get_queryset().filter()).cache(timeout=60 * 60 * 1)  # cache 1 days
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')
