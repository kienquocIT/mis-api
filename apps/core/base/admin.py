from django.contrib import admin

from apps.core.base.models import ApplicationProperty


# Register your models here.
@admin.register(ApplicationProperty)
class CustomerStatusAdmin(admin.ModelAdmin):
    fields = ("title", "code", "application", "type", "content_type", "remark", "properties")
    search_fields = ("name",)
    list_display = ("title", "code", "application", "type", "content_type", "remark", "properties")