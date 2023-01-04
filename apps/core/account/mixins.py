from django.db import transaction
from apps.shared import ResponseController
from rest_framework.exceptions import ValidationError


class AccountListMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(serializer.data, key_data='result')


class AccountCreateMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer, request.user)
        if not isinstance(instance, Exception):
            return ResponseController.created_201(self.serializer_class(instance).data)
        elif isinstance(instance, ValidationError):
            return ResponseController.internal_server_error_500()

    @classmethod
    def perform_create(cls, serializer, user_org):
        try:
            with transaction.atomic():
                instance = serializer.save(
                    user_created_id=user_org["user_id"],
                )
            return instance
        except Exception as e:
            print(e)
            return e

