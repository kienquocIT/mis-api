from django.contrib import admin
from django.utils.html import mark_safe

from apps.core.company.models import (
    Company, CompanyConfig, CompanyLicenseTracking, CompanyUserEmployee,
    CompanyFunctionNumber,
)
from apps.sharedapp.admin import AbstractAdmin


@admin.register(Company)
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
        'logo_icon_preview', 'title', 'code', 'date_created', 'tenant',
        'license_usage', 'total_user', 'software_start_using_time',
        'sub_domain',
    )
    search_fields = ('title', 'code', 'sub_domain')
    list_filter = ['tenant']
    ordering = ['title']
    date_hierarchy = 'date_created'


@admin.register(CompanyConfig)
class CompanyConfigAdmin(AbstractAdmin):
    list_display = (
        'company', 'language', 'currency',
        'definition_inventory_valuation', 'default_inventory_value_method',
        'cost_per_warehouse', 'cost_per_lot', 'cost_per_project',
    )
    list_filter = ['language', 'currency']


@admin.register(CompanyLicenseTracking)
class CompanyLicenseTrackingAdmin(AbstractAdmin):
    list_display = [field.name for field in CompanyLicenseTracking._meta.fields if field.name != 'id']
    list_filter = ['company', 'user', 'license_plan']


@admin.register(CompanyUserEmployee)
class CompanyUserEmployeeAdmin(AbstractAdmin):
    list_display = [field.name for field in CompanyUserEmployee._meta.fields if field.name != 'id']
    list_filter = ['company', 'user', 'employee']


@admin.register(CompanyFunctionNumber)
class CompanyFunctionNumberAdmin(AbstractAdmin):
    list_display = [
        'company', 'function', 'numbering_by', 'schema',
    ]
    list_filter = ['company__tenant']
