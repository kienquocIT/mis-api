from django.db import models
from .middleware import get_user_data


class NormalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class GlobalManager(models.Manager):
    def get_queryset(self):
        user_data = get_user_data()
        print('user_data: ', user_data)
        if user_data:
            return super().get_queryset().filter(mode=0, tenant_id=user_data['tenant_id'])
        return super().get_queryset().filter(mode=0)


class PrivateManager(models.Manager):
    def get_queryset(self):
        user_data = get_user_data()
        if user_data:
            return super().get_queryset().filter(mode=1, tenant_id=user_data['tenant_id'])
        return super().get_queryset().filter(mode=1)


class TeamManager(models.Manager):
    def get_queryset(self):
        user_data = get_user_data()
        if user_data:
            return super().get_queryset().filter(mode=2, tenant_id=user_data['tenant_id'])
        return super().get_queryset().filter(mode=2)
