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


class CompanyListMixin(BaseListMixin):

    def list_company_user_employee(self, request, *args, **kwargs):
        kwargs.update(self.setup_list_field_hidden(request.user))
        kwargs.update({'company_id': request.user.company_current_id})
        queryset = self.filter_queryset(self.get_queryset().filter(**kwargs))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_list(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_list(queryset, many=True)
        return ResponseController.success_200(data=serializer.data, key_data='result')
