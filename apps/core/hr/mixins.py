from rest_framework.exceptions import ValidationError

from django.db import transaction

from apps.shared import (
    ResponseController, BaseCreateMixin, BaseDestroyMixin, BaseListMixin, BaseRetrieveMixin,
    BaseUpdateMixin,
)
from apps.core.hr.models import RoleHolder


class HRListMixin(BaseListMixin):
    def list(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            queryset = self.filter_queryset(
                self.get_queryset()
                .filter(
                    mode=0,
                    tenant_id=request.user.tenant_current_id,
                    **kwargs
                )
            )
            serializer = self.serializer_list(queryset, many=True)  # pylint: disable=not-callable / E1102
            return ResponseController.success_200(
                getattr(serializer, 'data', None),
                key_data='result'
            )
        return ResponseController.unauthorized_401()

    def list_group_parent(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            if 'level' in kwargs:
                level = int(kwargs['level'])
                del kwargs['level']
                queryset = self.filter_queryset(
                    self.get_queryset()
                    .filter(
                        mode=0,
                        tenant_id=request.user.tenant_current_id,
                        group_level__level__lt=level,
                        **kwargs
                    )
                )
                serializer = self.serializer_class(queryset, many=True)  # pylint: disable=not-callable / E1102
                return ResponseController.success_200(serializer.data, key_data='result')
        return ResponseController.unauthorized_401()


class HRCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            serializer = self.serializer_create(data=request.data)  # pylint: disable=not-callable / E1102
            if hasattr(serializer, 'is_valid'):
                serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, request.user)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(
                    getattr(self.serializer_class(instance), 'data', None)  # pylint: disable=not-callable / E1102
                )
            if isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_create(cls, serializer, user):  # pylint: disable=W0237
        try:
            with transaction.atomic():
                instance = serializer.save(
                    user_created=user.id,
                    tenant_id=user.tenant_current_id,
                    company_id=user.company_current_id,
                )
            return instance
        except Exception as exc:
            print(exc)
            return exc


class HRRetrieveMixin(BaseRetrieveMixin):

    def retrieve(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs, is_delete=False)
            ).first()
            if instance:
                serializer = self.serializer_class(instance)  # pylint: disable=not-callable / E1102
                return ResponseController.success_200(getattr(serializer, 'data', None), key_data='result')
        return ResponseController.unauthorized_401()


class HRUpdateMixin(BaseUpdateMixin):
    serializer_update = None

    def update(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if instance:
                serializer = self.serializer_update(instance, data=request.data)  # pylint: disable=not-callable / E1102
                if hasattr(serializer, 'is_valid'):
                    serializer.is_valid(raise_exception=True)
                perform_update = self.perform_update(serializer)
                if not isinstance(perform_update, Exception):
                    return ResponseController.success_200(getattr(serializer, 'data', None), key_data='result')
                if isinstance(perform_update, ValidationError):
                    return ResponseController.internal_server_error_500()
            return ResponseController.notfound_404()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_update(cls, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save()
            return instance
        except Exception as exc:
            print(exc)
            return exc
        # return None


class HRDestroyMixin(BaseDestroyMixin):
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
            return ResponseController.notfound_404()
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
        except Exception as exc:
            print(exc)
        return False


class RoleCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            serializer = self.serializer_create(data=request.data)  # pylint: disable=not-callable / E1102
            if hasattr(serializer, 'is_valid'):
                serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, request.user)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(
                    getattr(self.serializer_detail(instance), 'data', None)  # pylint: disable=not-callable / E1102
                )
            if isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_create(cls, serializer, user):  # pylint: disable=W0237
        try:
            with transaction.atomic():
                instance = serializer.save(
                    user_created=user.id,
                    tenant_id=user.tenant_current_id,
                    company_id=user.company_current_id,
                )
            return instance
        except Exception as exc:
            print(exc)
            return exc


class RoleDestroyMixin(BaseDestroyMixin):
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
            return ResponseController.notfound_404()
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
        except Exception as exc:
            print(exc)
        return False
