from apps.core.base.models import PlanApplication
from apps.core.tenant.models import TenantPlan
from apps.shared import ResponseController, BaseListMixin


class ApplicationListMixin(BaseListMixin):
    def tenant_application_list(self, request, *args, **kwargs):
        kwargs.update(self.setup_list_field_hidden(request.user))
        tenant_plan_id_list = TenantPlan.objects.filter(
            tenant_id=request.user.tenant_current_id
        ).values_list(
            'plan__id',
            flat=True
        )
        plan_application_id_list = PlanApplication.object_normal.filter(
            plan_id__in=tenant_plan_id_list
        ).values_list(
            'application__id',
            flat=True
        )
        if plan_application_id_list:
            kwargs.update({'id__in': plan_application_id_list})
        queryset = self.filter_queryset(self.get_queryset().filter(**kwargs))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_list(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_list(queryset, many=True)
        return ResponseController.success_200(data=serializer.data, key_data='result')
