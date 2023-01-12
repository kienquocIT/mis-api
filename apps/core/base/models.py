from django.db import models

from apps.shared import BaseModel, M2MModel


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


class PlanApplication(M2MModel):
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE
    )
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Plan Application'
        verbose_name_plural = 'Plan Applications'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
