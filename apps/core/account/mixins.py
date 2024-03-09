from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.core.company.models import Company
from apps.core.account.models import User
from apps.shared import ResponseController, BaseCreateMixin, BaseDestroyMixin, BaseListMixin


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
    @staticmethod
    def sync_new_user_to_map(user_obj, company_id):
        raise NotImplementedError

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        if hasattr(serializer, 'is_valid'):
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer, request.user)
            self.sync_new_user_to_map(instance, request.data.get('company_current', None))
            if not isinstance(instance, Exception):
                return ResponseController.created_201(self.get_serializer_detail(instance).data)
            if isinstance(instance, ValidationError):
                return ResponseController.internal_server_error_500()
            return ResponseController.bad_request_400(instance.args[1] if len(instance.args) > 1 else 'Server Errors')
        return ResponseController.internal_server_error_500()

    @classmethod
    def perform_create(cls, serializer, user):  # pylint: disable=W0237
        # arguments-renamed / W0237
        try:
            with transaction.atomic():
                instance = serializer.save(
                    tenant_current_id=user.tenant_current_id,
                )
            return instance
        except Exception as err:
            return err


class AccountDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_admin_tenant:
            return ResponseController.internal_server_error_500(msg="Cannot delete user admin")
        self.perform_destroy(instance)
        return ResponseController.success_200({}, key_data='result')

    @staticmethod
    def perform_destroy(instance, is_purge=False):
        if is_purge is True:
            ...
        if instance.company_current_id:
            company_current_id = instance.company_current_id

            instance.delete()

            company = Company.objects.get(id=company_current_id)
            company.total_user = User.objects.filter(company_current=company_current_id).count()
            company.save()
