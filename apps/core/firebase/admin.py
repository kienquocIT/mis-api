from django.contrib import admin
from apps.sharedapp.admin import AbstractAdmin, my_admin_site
from apps.core.firebase.models import DeviceToken


@admin.register(DeviceToken, site=my_admin_site)
class DeviceTokenAdmin(AbstractAdmin):
    date_hierarchy = 'date_modified'
    list_display = [
        'company', 'user', 'is_active', 'created_at', 'date_modified',
    ]
    list_filter = [
        'is_active',
        'company',
    ]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            all_fields = [field.name for field in obj._meta.fields]
            readonly_fields = [field for field in all_fields if field != 'is_active']
            return readonly_fields
        return []

    @classmethod
    def check_user(cls, request):
        if request.user and hasattr(request.user, 'username_auth'):
            if request.user.username_auth == "admin-admin":
                return True
        return False

    def has_change_permission(self, request, obj=None):
        return self.check_user(request)

    def has_delete_permission(self, request, obj=None):
        return self.check_user(request)
