from django.db import transaction
from apps.shared import ResponseController
from rest_framework.exceptions import ValidationError


class HRListMixin:

    #     @MixinController.authenticate_request
    #     def list(self, request, *args, **kwargs):
    #         return MixinController.list_full_action(
    #             mixin_self=self,
    #             request=request,
    #             list_or_detail='list',
    #             is_singleton=True,
    #         )

    def list(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            queryset = self.get_queryset()
            if queryset:
                serializer = self.serializer_class(queryset, many=True)
                return ResponseController.success_200(serializer.data, key_data='result')
        return ResponseController.unauthorized_401()


class HRCreateMixin:

    def create(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            serializer = self.serializer_create(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, request.user)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(self.serializer_class(instance).data)
            elif isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_create(cls, serializer, user):
        try:
            with transaction.atomic():
                instance = serializer.save(
                    user_created=user.id,
                    tenant_id=user.tenant_current_id,
                    company_id=user.company_current_id,
                )
            return instance
        except Exception as e:
            print(e)
            return e


class HRRetrieveMixin:

    def retrieve(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs, is_delete=False)
            ).first()
            if instance:
                serializer = self.serializer_class(instance)
                return ResponseController.success_200(serializer.data, key_data='result')
            raise ResponseController.notfound_404()
        return ResponseController.unauthorized_401()


class HRUpdateMixin:

    def update(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if instance:
                serializer = self.serializer_class(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                perform_update = self.perform_update(serializer)
                if not isinstance(perform_update, Exception):
                    return ResponseController.success_200(serializer.data, key_data='result')
                elif isinstance(perform_update, ValidationError):
                    return ResponseController.internal_server_error_500()
            raise ResponseController.notfound_404()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_update(cls, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save()
            return instance
        except Exception as e:
            print(e)
            return e
        # return None
