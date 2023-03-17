from django.db import models
from jsonfield import JSONField

from apps.core.models import CoreAbstractModel


class Space(CoreAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    application = JSONField(default=[])
    is_system = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Space'
        verbose_name_plural = 'Space'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
