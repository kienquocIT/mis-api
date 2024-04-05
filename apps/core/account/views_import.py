from drf_yasg.utils import swagger_auto_schema

from apps.core.account.models import User
from apps.core.account.serializers_import import UserImportSerializer, UserImportReturnSerializer
from apps.shared import BaseCreateMixin, mask_view


class CoreAccountUserImport(BaseCreateMixin):
    queryset = User.objects
    serializer_create = UserImportSerializer
    serializer_detail = UserImportReturnSerializer
    create_hidden_field = ['tenant_current_id']

    @swagger_auto_schema(operation_summary='Create New User', request_body=UserImportSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='account', model_code='user', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'tenant_current': request.user.tenant_current,
            'company_current': request.user.company_current,
            'user_obj': request.user,
        }
        return self.create(request, *args, **kwargs)
