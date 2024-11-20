__all__ = ['AbstractAdmin']

from django.contrib import admin


class AbstractAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Company._meta.fields if field.name != 'id']
    # list_display = [field.name for field in Company._meta.fields if field.name not in ['id']]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    class Meta:
        abstract = True
