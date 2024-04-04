from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.models import GroupLevel, Group
from apps.core.hr.serializers.fimport import (
    GroupImportSerializer, GroupLevelImportReturnSerializer,
    GroupImportReturnSerializer, GroupLevelImportSerializer,
)
from apps.shared import BaseCreateMixin, mask_view


class GroupLevelImport(BaseCreateMixin):
    queryset = GroupLevel.objects

    serializer_detail = GroupLevelImportReturnSerializer
    serializer_create = GroupLevelImportSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Group Level",
        operation_description="Import new group level",
        request_body=GroupLevelImportSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hr', model_code='group', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'company_current_id': request.user.company_current_id,
        }
        return self.create(request, *args, **kwargs)


class GroupImport(BaseCreateMixin):
    queryset = Group.objects

    serializer_detail = GroupImportReturnSerializer
    serializer_create = GroupImportSerializer
    create_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Import Group",
        operation_description="Import new group",
        request_body=GroupImportSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='hr', model_code='group', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
