from django.contrib import admin

from apps.core.base.models import ApplicationProperty


# Register your models here.
@admin.register(ApplicationProperty)
class CustomerStatusAdmin(admin.ModelAdmin):
    def title_with_appname(self, obj):
        return ("%s (%s)" % (obj.title, obj.application))

    fields = ("title", "code", "application", "type", "content_type", "remark", "properties")
    search_fields = ("name",)
    list_display = ("title_with_appname", "code", "application", "type", "content_type", "remark", "properties")
