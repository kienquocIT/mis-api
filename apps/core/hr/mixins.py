from rest_framework.exceptions import ValidationError

from django.db import transaction

from apps.shared import (
    ResponseController, BaseCreateMixin, BaseDestroyMixin, BaseListMixin, BaseRetrieveMixin,
    BaseUpdateMixin,
)
from apps.core.hr.models import RoleHolder


class HRListMixin(BaseListMixin):
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
                serializer = self.serializer_class.__class__(queryset, many=True)
                return ResponseController.success_200(serializer.data, key_data='result')
        return ResponseController.unauthorized_401()


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
            serializer = self.serializer_create.__class__(data=request.data)
            if hasattr(serializer, 'is_valid'):
                serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, request.user)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(getattr(self.serializer_detail.__class__(instance), 'data', None))
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
