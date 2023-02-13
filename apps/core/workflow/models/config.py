from django.db import models
from jsonfield import JSONField

from apps.shared import TenantCoreModel


class Workflow(TenantCoreModel):
    code_application = models.TextField(
        verbose_name="code application",
        null=True,
        help_text="code of application in base"
    )
    is_active = models.BooleanField(
        verbose_name='active status',
        default=True
    )
    is_multi_company = models.BooleanField(
        verbose_name='Multi company',
        default=False
    )

    class Meta:
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Zone(TenantCoreModel):
    workflow = models.ForeignKey(
        'workflow.Workflow',
        on_delete=models.CASCADE,
        related_name="zone_workflow",
        null=False
    )
    name = models.TextField(
        verbose_name="name",
        required=True
    )
    remark = models.TextField(
        verbose_name="description",
        required=False
    )
    zone_field = JSONField(
        verbose_name="zone field",
        required=True,
        default=[]
    )

    class Meta:
        verbose_name = 'Zone in workflow'
        verbose_name_plural = 'Zone in workflow'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
