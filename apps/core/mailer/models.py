from uuid import UUID

from django.db import models
from django.db.models import Count

from apps.core.mailer.handle_html import HTMLController
from apps.shared import MasterDataAbstractModel

MAIL_TEMPLATE_SYSTEM_CODE = (
    (1, 'Welcome'),
    (2, 'Calendar'),
)


class MailTemplateSystem(MasterDataAbstractModel):
    system_code = models.CharField(max_length=2, help_text='MAIL_TEMPLATE_SYSTEM_CODE')
    contents = models.TextField(blank=True)

    @classmethod
    def template_get_or_create(cls, tenant_id, company_id, system_code):
        obj, _created = MailTemplateSystem.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, system_code=system_code,
            defaults={
                'is_active': False,
                'contents': '',
            }
        )
        return obj

    def save(self, *args, **kwargs):
        self.contents = HTMLController(html_str=self.contents).clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Mail Template System'
        verbose_name_plural = 'Mail Template System'
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        unique_together = ('tenant_id', 'company_id', 'system_code')


class MailTemplate(MasterDataAbstractModel):
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)
    contents = models.TextField()
    is_default = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    @classmethod
    def check_using_unique(cls, tenant_id: UUID, company_id: UUID) -> (bool, list[str]):
        app_not_unique = []
        kw_arg = {'tenant_id': tenant_id, 'company_id': company_id, 'is_default': True}
        for data in MailTemplate.objects.filter(**kw_arg).values('application').annotate(total=Count('id')):
            if data['total'] > 1:
                app_not_unique.append(data['application'])

        if app_not_unique:
            return False, app_not_unique
        return True, []

    def confirm_unique_using(self):
        obj_running_using = MailTemplate.objects.filter(
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
        verbose_name = 'Mail Template'
        verbose_name_plural = 'Mail Template'
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
