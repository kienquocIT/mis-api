from django.db import transaction

from apps.core.company.models import Company, CompanyUserEmployee
from apps.core.account.models import User
from apps.shared import ResponseController, BaseCreateMixin, BaseDestroyMixin, BaseListMixin
from rest_framework.exceptions import ValidationError


class AccountListMixin(BaseListMixin):
    @staticmethod
    def setup_hidden(fields: list, user) -> dict:
        ctx = {}
        for key in fields:
            data = None
            match key:
                case 'tenant_current_id':
                    data = user.tenant_current_id
                case 'tenant_current':
                    data = user.tenant_current
                case 'company_current_id':
                    data = user.company_current_id
                case 'company_current':
                    data = user.company_current
                case 'space_current_id':
                    data = user.space_current_id
                case 'space_current':
                    data = user.space_current
                case 'employee_current_id':
                    data = user.employee_current_id
                case 'employee_current':
                    data = user.employee_current
            if data is not None:
                ctx[key] = data
        return ctx


class AccountCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer, request.user)
        self.sync_new_user_to_map(instance, request.data.get('company_current', None))
        if not isinstance(instance, Exception):
            return ResponseController.created_201(self.serializer_detail(instance).data)
        elif isinstance(instance, ValidationError):
            return ResponseController.internal_server_error_500()
        else:
            return ResponseController.bad_request_400(instance.args[1])

    @classmethod
    def perform_create(cls, serializer, user):
        try:
            with transaction.atomic():
                instance = serializer.save(
                    tenant_current_id=user.tenant_current_id,
                )
                if instance.company_current_id:
                    company_added_id = instance.company_current_id
                    company = Company.object_normal.get(id=company_added_id)
                    company.total_user = CompanyUserEmployee.object_normal.filter(company_id=company_added_id).count()+1
                    company.save()
            return instance
        except Exception as e:
            return e


class AccountDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_admin_tenant:
            return ResponseController.internal_server_error_500(msg="Cannot delete user admin")
        self.perform_destroy(instance)
        return ResponseController.success_200({}, key_data='result')

    @staticmethod
    def perform_destroy(instance):
        if instance.company_current_id:
            company_current_id = instance.company_current_id

            instance.delete()

            company = Company.object_normal.get(id=company_current_id)
            company.total_user = User.objects.filter(company_current=company_current_id).count()
            company.save()
