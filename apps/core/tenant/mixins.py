from django.db import transaction
from apps.shared import ResponseController
from apps.core.tenant.serializers import CompanyCreateSerializer
from rest_framework.exceptions import ValidationError
from apps.core.tenant.models import Tenant


# Company
class CompanyCreateMixin:

    def create(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            data = request.data
            tenant = Tenant.objects.get(admin_id=request.user.id)
            data.update({'tenant_id': tenant})
            data.update({'code': 'TEST001'})
            serializer = CompanyCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(CompanyCreateSerializer(instance).data)
            elif isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
        return ResponseController.unauthorized_401()

    def perform_create(self, serializer):
        instance = serializer.save(title=self.request.data.get('title', None),
                                   code=self.request.data.get('code', None),
                                   tenant=self.request.data.get('tenant_id', None))
        return instance
