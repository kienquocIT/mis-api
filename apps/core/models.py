from django.db import models
from django.utils import timezone

from apps.shared import SimpleAbstractModel, FORMATTING

__all__ = ['CoreAbstractModel', 'TenantAbstractModel']


# account, plan, app, tenant, company --> move to core models.py
class CoreAbstractModel(SimpleAbstractModel):
    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    title = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100, blank=True)

    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} - {self.code}'

    def get_detail(self, excludes=None):
        return self._get_detail(excludes=excludes)

    def _get_detail(self, excludes=None):
        if not isinstance(excludes, list):
            excludes = []
        result = {
            'id': str(self.id),
            'title': str(self.title) if self.title else None,
            'code': str(self.code) if self.code else None,
            'date_created': FORMATTING.parse_datetime(self.date_created),
            'date_modified': FORMATTING.parse_datetime(self.date_modified),
        }
        if excludes:
            for f_name in excludes:
                result.pop(f_name)
        return result


# employee, role, group  --> move to core models.py
class TenantAbstractModel(SimpleAbstractModel):
    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    title = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100, blank=True)

    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    date_modified = models.DateTimeField(
        auto_now_add=True,
        help_text='Date modified this record in last',
    )

    # system flag
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
