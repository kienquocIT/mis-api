from django.db import transaction
from apps.core.company.models import Company
from apps.core.tenant.models import Tenant
from rest_framework.exceptions import ValidationError
from apps.shared import ResponseController, BaseDestroyMixin, BaseCreateMixin


class CompanyCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer, request.user)
        if not isinstance(instance, Exception):
            return ResponseController.created_201(self.serializer_class(instance).data)
        elif isinstance(instance, ValidationError):
            return ResponseController.internal_server_error_500()

    @classmethod
    def perform_create(cls, serializer, user):
        try:
            with transaction.atomic():
                if user.tenant_current_id:
                    tenant_current_id = user.tenant_current_id

                    instance = serializer.save(
                        tenant_id=tenant_current_id,
                        user_created=user.id,
                        user_modified=user.id,
                    )

                    tenant = Tenant.object_normal.get(id=tenant_current_id)
                    tenant.company_total = Company.object_normal.filter(tenant_id=tenant_current_id).count()
                    tenant.save()
            return instance
        except Exception as e:
            print(e)
            return e


class CompanyDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        if request.user.tenant_current_id:
            instance = self.get_object()
            instance.delete()

            tenant_current_id = request.user.tenant_current_id
            tenant = Tenant.object_normal.get(id=tenant_current_id)
            tenant.company_total = Company.object_normal.filter(tenant_id=tenant_current_id).count()
            tenant.save()

            return ResponseController.success_200({}, key_data='result')

        return ResponseController.internal_server_error_500()
