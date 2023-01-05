from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.core.tenant.mixins import CompanyCreateMixin, CompanyListMixin
from apps.core.tenant.models import Company

from apps.core.tenant.serializers import CompanyCreateSerializer


# Company
class CompanyList(
    CompanyListMixin,
    CompanyCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Company.object_normal

    serializer_create = CompanyCreateSerializer

    @swagger_auto_schema(
        operation_summary="Company list",
        operation_description="Company list",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Company",
        operation_description="Create new Company",
        request_body=CompanyCreateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
