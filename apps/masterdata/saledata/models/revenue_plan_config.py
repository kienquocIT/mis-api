from django.db import models
from apps.shared import MasterDataAbstractModel


class RevenuePlanConfig(MasterDataAbstractModel):
    # [id, id, id]
    roles_mapped_list = models.JSONField(
        default=list
    )

    class Meta:
        verbose_name = 'RevenuePlanConfig'
        verbose_name_plural = 'RevenuePlanConfig'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RevenuePlanConfigRoles(MasterDataAbstractModel):
    revenue_plan_config = models.ForeignKey(
        'RevenuePlanConfig',
        related_name='revenue_plan_config_mapped',
        on_delete=models.CASCADE,
        null=True
    )
    roles_mapped = models.ForeignKey(
        'hr.Role',
        related_name='roles_mapped',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'RevenuePlanConfigRoles'
        verbose_name_plural = 'RevenuePlanConfigRoles'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
