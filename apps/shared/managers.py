from django.contrib.auth.models import AnonymousUser
from django.db import models
from crum import get_current_user


class NormalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class GlobalManager(models.Manager):
    def get_queryset(self):
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            return super().get_queryset().filter(mode=0, tenant_id=user_obj.tenant_current_id)
        return super().get_queryset().filter(mode=0)


class PrivateManager(models.Manager):
    def get_queryset(self):
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            return super().get_queryset().filter(mode=1, tenant_id=user_obj.tenant_current_id)
        return super().get_queryset().filter(mode=1)


class TeamManager(models.Manager):
    def get_queryset(self):
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            return super().get_queryset().filter(mode=2, tenant_id=user_obj.tenant_current_id)
        return super().get_queryset().filter(mode=2)
