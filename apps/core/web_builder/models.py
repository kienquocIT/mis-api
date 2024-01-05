from django.db import models

from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


class PageTemplate(SimpleAbstractModel):
    title = models.CharField(max_length=100)
    image = models.TextField(blank=True)
    project_data = models.JSONField(blank=True)

    class Meta:
        verbose_name = 'Page Template'
        verbose_name_plural = 'Page Template'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()


class PageBuilder(MasterDataAbstractModel):
    remarks = models.TextField(blank=True, null=True)
    page_path = models.CharField(max_length=200)
    page_title = models.CharField(max_length=100)
    is_publish = models.BooleanField(default=False)

    # page HTML CSS
    page_html = models.TextField(blank=True)
    page_css = models.TextField(blank=True)
    page_js = models.TextField(blank=True)
    page_full = models.TextField(blank=True)
    project_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Page Builder'
        verbose_name_plural = 'Page Builder'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant_id', 'company_id', 'page_path',)
