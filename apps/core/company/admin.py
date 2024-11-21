from django.contrib import admin
from django.utils.html import mark_safe

from apps.core.company.models import (
    Company, CompanyConfig, CompanyLicenseTracking, CompanyUserEmployee,
    CompanyFunctionNumber,
)
from apps.sharedapp.admin import AbstractAdmin, my_admin_site


@admin.register(Company, site=my_admin_site)
class CompanyAdmin(AbstractAdmin):
    @classmethod
    def logo_icon_preview(cls, obj):
        html_img = ''
        if obj.logo:
            html_img += f'<img src="{obj.logo.url}" width="100" />'
        if obj.icon:
            html_img += f'<img src="{obj.icon.url}" width="30" height="30" />'
        return mark_safe(html_img) if html_img else "-"

    list_display = (
        'title', 'code', 'logo_icon_preview', 'date_created', 'tenant',
        'license_usage', 'total_user', 'software_start_using_time',
        'sub_domain',
    )
    search_fields = ('title', 'code', 'sub_domain')
    list_filter = ['tenant']
    ordering = ['title']
    date_hierarchy = 'date_created'

    @classmethod
    def total_user_recheck(cls, obj):
        return CompanyUserEmployee.objects.filter(company=obj, user__isnull=False).count()

    @classmethod
    def total_employee_recheck(cls, obj):
        return CompanyUserEmployee.objects.filter(company=obj, employee__isnull=False).count()

    @classmethod
    def employee_linked_in_all(cls, obj):
        linked = CompanyUserEmployee.objects.filter(company=obj, employee__isnull=False, user__isnull=False).count()
        all_count = CompanyUserEmployee.objects.filter(company=obj).count()
        return f'{linked}/{all_count}'

    fields = [
        'title', 'code',
        'logo_icon_preview',
        'date_created', 'date_modified',
        'tenant', 'license_usage', 'total_user',
        'total_user_recheck', 'total_employee_recheck', 'employee_linked_in_all',
        'representative_fullname', 'address', 'email', 'software_start_using_time', 'phone', 'fax',
        'media_company_id', 'media_company_code', 'sub_domain',
    ]


@admin.register(CompanyConfig, site=my_admin_site)
class CompanyConfigAdmin(AbstractAdmin):
    list_display = (
        'company', 'language', 'currency',
        'definition_inventory_valuation', 'default_inventory_value_method',
        'cost_per_warehouse', 'cost_per_lot', 'cost_per_project',
    )
    list_filter = ['language', 'currency']


@admin.register(CompanyLicenseTracking, site=my_admin_site)
class CompanyLicenseTrackingAdmin(AbstractAdmin):
    list_display = [field.name for field in CompanyLicenseTracking._meta.fields if field.name != 'id']
    list_filter = ['company', 'user', 'license_plan']


@admin.register(CompanyUserEmployee, site=my_admin_site)
class CompanyUserEmployeeAdmin(AbstractAdmin):
    list_display = [field.name for field in CompanyUserEmployee._meta.fields if field.name != 'id']
    list_filter = ['company', 'user', 'employee']


@admin.register(CompanyFunctionNumber, site=my_admin_site)
class CompanyFunctionNumberAdmin(AbstractAdmin):
    list_display = [
        'company', 'function', 'numbering_by', 'schema',
    ]
    list_filter = ['company__tenant']
