from django.db import models
from jsonfield import JSONField

from apps.shared import TenantCoreModel


class Workflow(TenantCoreModel):
    code_application = models.TextField(
        verbose_name="code application",
        null=True,
        help_text="code of application in base"
    )

    class Meta:
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

