from django.contrib import admin

from apps.core.base.models import ApplicationProperty
from apps.sharedapp.admin import AbstractAdmin, my_admin_site


@admin.register(ApplicationProperty, site=my_admin_site)
class CustomerStatusAdmin(AbstractAdmin):
    @classmethod
    def title_with_appname(cls, obj):
        return f"{obj.title} ({obj.application})"

    fields = ("title", "code", "application", "type", "content_type", "remark", "properties")
    search_fields = ("name",)
    list_display = ("title_with_appname", "code", "application", "type", "content_type", "remark", "properties")
