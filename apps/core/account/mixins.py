from django.db import transaction
from apps.shared import ResponseController, BaseCreateMixin, BaseDestroyMixin
from rest_framework.exceptions import ValidationError


class AccountCreateMixin(BaseCreateMixin):
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
                instance = serializer.save(
                    tenant_current_id=user.tenant_current_id,
                )
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
        instance.delete()

