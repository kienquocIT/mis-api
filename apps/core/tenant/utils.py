from apps.core.base.models import Application
from apps.core.tenant.models import TenantPlan

__all__ = ['PlanController']


class PlanController:
    @classmethod
    def get_plan_of_tenant(cls, tenant_id) -> list:
        if tenant_id:
            return TenantPlan.objects.filter(tenant_id=tenant_id).values_list('plan_id', flat=True)
        return []

    @classmethod
    def get_app(cls, app_ids) -> list:
        if app_ids:
            return Application.objects.filter(id__in=app_ids).values_list('id', flat=True)
        return []
