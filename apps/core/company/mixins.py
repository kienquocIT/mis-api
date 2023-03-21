from apps.core.company.models import Company
from apps.core.tenant.models import Tenant
from apps.shared import ResponseController, BaseDestroyMixin, BaseListMixin


class CompanyDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        if request.user.tenant_current_id:
            instance = self.get_object()
            instance.delete()

            tenant_current_id = request.user.tenant_current_id
            tenant = Tenant.objects.get(id=tenant_current_id)
            tenant.company_total = Company.objects.filter(tenant_id=tenant_current_id).count()
            tenant.save()

            return ResponseController.success_200({}, key_data='result')

        return ResponseController.internal_server_error_500()
