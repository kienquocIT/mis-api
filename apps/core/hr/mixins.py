from django.db import transaction
from apps.shared import ResponseController
from rest_framework.exceptions import ValidationError
from apps.core.hr.models import RoleHolder


class HRListMixin(object):
    def list(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            queryset = self.filter_queryset(
                self.get_queryset()
                .filter(**kwargs)
            )
            serializer = self.serializer_class(queryset, many=True)
            return ResponseController.success_200(serializer.data, key_data='result')
        return ResponseController.unauthorized_401()


class HRCreateMixin(object):
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


class HRDestroyMixin:
    def destroy(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if instance:
                state = self.perform_destroy(instance)
                if state:
                    return ResponseController.no_content_204()
                return ResponseController.internal_server_error_500()
            raise ResponseController.notfound_404()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_destroy(cls, instance, purge=False):
        try:
            with transaction.atomic():
                if purge:
                    instance.delete()
                    return True
                instance.is_delete = True
                instance.save()
            return True
        except Exception as e:
            print(e)
        return False


class RoleListMixin:

    def list(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            queryset = self.filter_queryset(
                self.get_queryset()
                .filter(**kwargs)
            )
            if queryset:
                serializer = self.serializer_class(queryset, many=True)
                return ResponseController.success_200(serializer.data, key_data='result')
            return ResponseController.success_200({}, key_data='result')
        return ResponseController.unauthorized_401()


class RoleCreateMixin:
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


class RoleRetrieveMixin:

    def retrieve(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if instance:
                serializer = self.serializer_class(instance)
                return ResponseController.success_200(serializer.data, key_data='result')
            raise ResponseController.notfound_404()
        return ResponseController.unauthorized_401()


class RoleUpdateMixin:

    def update(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if instance:
                serializer = self.serializer_update(instance, data=request.data)
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
            return e
        # return None


class RoleDestroyMixin:
    def destroy(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if instance:
                state = self.perform_destroy(instance)
                if state:
                    return ResponseController.success_200({'detail': 'success'}, key_data='result')
                return ResponseController.internal_server_error_500()
            raise ResponseController.notfound_404()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_destroy(cls, instance, purge=True):
        try:
            with transaction.atomic():
                if purge:
                    role_holder = RoleHolder.object_normal.filter(role=instance)
                    if role_holder:
                        role_holder.delete()
                    instance.delete()
                    return True
                instance.is_delete = True
                instance.save()
            return True
        except Exception as e:
            print(e)
        return False
