from django.db import models

from apps.shared import BaseModel


class SubscriptionPlan(BaseModel):
    class Meta:
        verbose_name = 'Subscription Plan'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()


class Application(BaseModel):
    remarks = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Application'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
