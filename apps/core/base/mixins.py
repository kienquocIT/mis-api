from apps.core.base.models import PlanApplication
from apps.shared import ResponseController, BaseListMixin


class ApplicationListMixin(BaseListMixin):
    def tenant_application_list(self, request, *args, **kwargs):
        filter_kwargs = {
            **kwargs,
            **self.cls_check.attr.setup_hidden(from_view='list'),
        }
        plan_application_id_list = PlanApplication.objects.filter(
            plan_id__in=request.user.tenant_current.tenant_plan_tenant.values_list('plan__id', flat=True)
        ).values_list('application__id', flat=True)
        if plan_application_id_list:
            filter_kwargs.update({'id__in': plan_application_id_list})
        queryset = self.filter_queryset(self.get_queryset().filter(**filter_kwargs))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_list(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_list(queryset, many=True)
        return ResponseController.success_200(data=serializer.data, key_data='result')
