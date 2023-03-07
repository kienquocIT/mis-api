from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.core.company.models import Company
from apps.core.tenant.models import Tenant
from apps.shared import ResponseController, BaseDestroyMixin, BaseCreateMixin, BaseListMixin


class CompanyCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        tenant_current_id = request.user.tenant_current_id
        current_tenant = Tenant.object_normal.get(id=tenant_current_id)
        company_quantity_max = current_tenant.company_quality_max
        current_company_quantity = current_tenant.company_total

        if company_quantity_max > current_company_quantity:
            serializer = self.serializer_create(data=request.data)  # pylint: disable=not-callable / E1102
            if hasattr(serializer, 'is_valid'):
                serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, request.user)
            if not isinstance(instance, Exception):
                return ResponseController.created_201(
                    getattr(
                        self.serializer_class(instance),  # pylint: disable=not-callable / E1102
                        'data',
                        None
                    )
                )
            if isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
        return ResponseController.forbidden_403(msg='Maximum 5 companies only')

    @classmethod
    def perform_create(cls, serializer, user):  # pylint: disable=W0237
        try:
            with transaction.atomic():
                if user.tenant_current_id:
                    tenant_current_id = user.tenant_current_id

                    instance = serializer.save(
                        tenant_id=tenant_current_id,
                        user_created=user.id,
                        user_modified=user.id,
                    )

                    tenant = Tenant.object_normal.get(id=tenant_current_id)
                    tenant.company_total = Company.object_normal.filter(tenant_id=tenant_current_id).count()
                    tenant.save()
            return instance
        except Exception as exc:
            print(exc)
            return exc


class CompanyDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        if request.user.tenant_current_id:
            instance = self.get_object()
            instance.delete()

            tenant_current_id = request.user.tenant_current_id
            tenant = Tenant.object_normal.get(id=tenant_current_id)
            tenant.company_total = Company.object_normal.filter(tenant_id=tenant_current_id).count()
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
