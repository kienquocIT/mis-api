from django.db import models


class NormalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class GlobalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mode=0)


class PrivateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mode=1)


class TeamManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mode=2)
