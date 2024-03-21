from uuid import UUID

from django.db import models
from django.db.models import Count

from apps.core.mailer.handle_html import HTMLController
from apps.shared import MasterDataAbstractModel


class PrintTemplates(MasterDataAbstractModel):
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)
    contents = models.TextField()
    is_default = models.BooleanField(default=False)  # mean change from using to default
    remarks = models.TextField(blank=True)

    @classmethod
    def check_using_unique(cls, tenant_id: UUID, company_id: UUID) -> (bool, list[str]):
        app_not_unique = []
        kw_arg = {'tenant_id': tenant_id, 'company_id': company_id, 'is_default': True}
        for data in PrintTemplates.objects.filter(**kw_arg).values('application').annotate(total=Count('id')):
            if data['total'] > 1:
                app_not_unique.append(data['application'])

        if app_not_unique:
            return False, app_not_unique
        return True, []

    def confirm_unique_using(self):
        obj_running_using = PrintTemplates.objects.filter(
            tenant=self.tenant, company=self.company, application=self.application, is_default=True
        ).exclude(id=self.id)
        for obj in obj_running_using:
            obj.is_default = False
            obj.save(update_fields=['is_default'])
        return True

    def save(self, *args, **kwargs):
        if self.is_default is True:
            self.is_active = True
            self.confirm_unique_using()
        self.contents = HTMLController(html_str=self.contents).clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Print Templates'
        verbose_name_plural = 'Print Templates'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()
