from django.contrib import admin
from django.utils.html import mark_safe
from apps.sharedapp.admin import AbstractAdmin
from apps.core.account.models import User, VerifyContact, ValidateUser, TOTPUser


@admin.register(User)
class UserAdmin(AbstractAdmin):
    list_display = (
        'username', 'first_name', 'last_name',
        'email', 'phone', 'last_login', 'is_active', 'date_created',
        'is_admin_tenant', 'tenant_current', 'company_current', 'employee_current',  # 'space_current',
        'auth_2fa', 'auth_locked_out',
    )
    search_fields = ('id', 'username', 'email', 'phone', 'full_name_search')
    list_filter = ('is_active', 'auth_2fa', 'auth_locked_out', 'is_admin_tenant', 'tenant_current', 'company_current')
    ordering = ['username']
    date_hierarchy = 'last_login'


@admin.register(VerifyContact)
class VerifyContactAdmin(AbstractAdmin):
    list_display = [field.name for field in VerifyContact._meta.fields if field.name != 'id']


@admin.register(ValidateUser)
class ValidateUserAdmin(AbstractAdmin):
    list_display = [field.name for field in ValidateUser._meta.fields if field.name != 'id']


@admin.register(TOTPUser)
class TOTPUserAdmin(AbstractAdmin):
    list_display = [
        'user', 'confirmed', 'enabled', 'locked_out', 'last_used_at', 'date_created', 'date_modified',
    ]
    list_filter = ['user', 'verified_success', 'verified_failed', 'enabled', 'locked_out', 'confirmed']
    date_hierarchy = 'last_used_at'

    @classmethod
    def pretty_verified_success(cls, obj):
        html_data = "".join([f'<li>{item}</li>' for item in obj.verified_success])
        return mark_safe(f'<ol>{html_data}</ol>')

    @classmethod
    def pretty_verified_failed(cls, obj):
        html_data = "".join([f'<li>{item}</li>' for item in obj.verified_failed])
        return mark_safe(f'<ol>{html_data}</ol>')

    fields = [
        'user', 'confirmed', 'enabled', 'locked_out', 'date_created', 'date_modified',
        'step', 't0', 'digits', 'tolerance', 'drift', 'last_t', 'throttling_failure_timestamp',
        'throttling_failure_count', 'last_used_at',
        'pretty_verified_success', 'pretty_verified_failed',
    ]
