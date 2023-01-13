from django.db import transaction

from apps.core.company.models import Company
from apps.core.account.models import User
from apps.shared import ResponseController, BaseCreateMixin, BaseDestroyMixin
from rest_framework.exceptions import ValidationError


class AccountCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer, request.user)
        self.sync_new_user_to_map(instance, request.user.company_current_id)
        if not isinstance(instance, Exception):
            return ResponseController.created_201(self.serializer_class(instance).data)
        elif isinstance(instance, ValidationError):
            return ResponseController.internal_server_error_500()

    @classmethod
    def perform_create(cls, serializer, user):
        try:
            with transaction.atomic():
                instance = serializer.save(
                    tenant_current_id=user.tenant_current_id,
                )
                if instance.company_current_id:
                    company_current_id = instance.company_current_id
                    company = Company.object_normal.get(id=company_current_id)
                    company.total_user = User.objects.filter(company_current=company_current_id).count()
                    company.save()
            return instance
        except Exception as e:
            print(e)
            return e


class AccountDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ResponseController.success_200({}, key_data='result')

    @staticmethod
    def perform_destroy(instance):
        if instance.company_current_id:
            company_current_id = instance.company_current_id

            instance.delete()

            company = Company.object_normal.get(id=company_current_id)
            company.total_user = User.objects.filter(company_current=company_current_id).count()
            company.save()
