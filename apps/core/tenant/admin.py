from django.contrib import admin
from apps.core.tenant.models import Tenant, TenantPlan
from apps.sharedapp.admin import AbstractAdmin, my_admin_site


@admin.register(Tenant, site=my_admin_site)
class TenantAdmin(AbstractAdmin):
    list_display = (
        'title', 'code', 'kind', 'sub_domain', 'company_quality_max', 'admin', 'company_total', 'date_created',
    )
    search_fields = ['title', 'code', 'sub_domain']
    ordering = ['title']
    date_hierarchy = 'date_created'


@admin.register(TenantPlan, site=my_admin_site)
class TenantPlanAdmin(AbstractAdmin):
    list_display = (
        'tenant', 'plan', 'purchase_order', 'date_active', 'date_end', 'is_limited', 'license_quantity', 'is_expired',
        'license_buy_type', 'date_created',
    )
    list_filter = ['tenant', 'plan']
