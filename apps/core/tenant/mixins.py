from django.db import transaction
from apps.shared import ResponseController
from apps.core.tenant.serializers import CompanyCreateSerializer, CompanyListSerializer
from rest_framework.exceptions import ValidationError
from apps.core.tenant.models import Tenant, Company


# Company
class CompanyListMixin:

    def list(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            tenant = Tenant.objects.get(admin_id=request.user.id)
            queryset = Company.objects.filter(tenant_id=tenant)
            if queryset:
                serializer = CompanyListSerializer(queryset, many=True)
                serializer.data[0].update({'is_auto_create_company': tenant.auto_create_company})
                return ResponseController.success_200(serializer.data, key_data='result')
        return ResponseController.unauthorized_401()


class CompanyCreateMixin:

    def create(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            data = request.data
            tenant = Tenant.objects.get(admin_id=request.user.id)
            data.update({'tenant': tenant})
            serializer = CompanyCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(CompanyCreateSerializer(instance).data)
            elif isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
        return ResponseController.unauthorized_401()

    def perform_create(self, serializer):
        instance = serializer.save(tenant=self.request.data.get('tenant', None),
                                   code=self.request.data.get('code', None),
                                   representative_fullname=self.request.data.get('representative_fullname', None),
                                   address=self.request.data.get('address', None),
                                   email=self.request.data.get('email', None),
                                   phone=self.request.data.get('phone', None))
        return instance
