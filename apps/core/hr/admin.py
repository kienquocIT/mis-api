from django.contrib import admin
from apps.sharedapp.admin import AbstractAdmin
from apps.core.hr.models import Employee, PlanEmployee, EmployeePermission, DistributionPlan, DistributionApplication


@admin.register(Employee)
class EmployeeAdmin(AbstractAdmin):
    list_display = [
        'first_name', 'last_name', 'code', 'email', 'phone',
        'user', 'is_admin_company', 'is_active', 'is_delete',
    ]
    list_filter = [
        'is_active',
        ("user", admin.EmptyFieldListFilter),
        'company',
    ]


@admin.register(PlanEmployee)
class PlanEmployeeAdmin(AbstractAdmin):
    list_display = [field.name for field in PlanEmployee._meta.fields if field.name not in ['id']]
    list_filter = [
        'employee', 'plan',
    ]


@admin.register(EmployeePermission)
class EmployeePermissionAdmin(AbstractAdmin):
    @classmethod
    def count_permission_by_id(cls, obj):
        return len(obj.permission_by_id.keys())

    @classmethod
    def count_permission_by_configured(cls, obj):
        return len(obj.permission_by_configured)

    @classmethod
    def count_permission_by_opp(cls, obj):
        return len(obj.permission_by_opp.keys())

    @classmethod
    def count_permission_by_project(cls, obj):
        return len(obj.permission_by_project.keys())

    list_display = [
        'employee',
        'count_permission_by_id', 'count_permission_by_configured',
        'count_permission_by_opp', 'count_permission_by_project',
    ]
    list_filter = ['employee']


@admin.register(DistributionPlan)
class DistributionPlanAdmin(AbstractAdmin):
    list_display = [
        'employee', 'plan', 'tenant_plan', 'date_created', 'is_active',
    ]
    list_filter = [
        'is_active', 'employee', 'company', 'tenant',
    ]


@admin.register(DistributionApplication)
class DistributionApplicationAdmin(AbstractAdmin):
    list_display = [
        'employee', 'app', 'distribution_plan', 'date_created', 'is_active'
    ]
    list_filter = [
        'is_active', 'employee', 'company', 'tenant',
    ]
