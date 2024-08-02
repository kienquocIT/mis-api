__all__ = ['ProjectConfig']

from django.db import models

from apps.shared import SimpleAbstractModel


class ProjectConfig(SimpleAbstractModel):
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.OneToOneField(
        'company.Company', on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_company',
    )
    person_can_end = models.JSONField(
        default=dict, verbose_name='list of employee can complete project',
        null=True
    )

    class Meta:
        verbose_name = 'Project config'
        verbose_name_plural = 'Project config of company'
        default_permissions = ()
        permissions = ()
