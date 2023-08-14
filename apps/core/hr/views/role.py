from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.hr.mixins import RoleDestroyMixin
from apps.core.hr.models import Role, Employee
from apps.core.hr.serializers.role_serializers import (
    RoleUpdateSerializer, RoleDetailSerializer,
    RoleCreateSerializer,
    RoleListSerializer,
)
from apps.shared import mask_view, BaseListMixin, BaseUpdateMixin, BaseRetrieveMixin, BaseCreateMixin


class RoleList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = Role.objects
    serializer_list = RoleListSerializer
    serializer_create = RoleCreateSerializer
    serializer_detail = RoleDetailSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id', 'tenant_id']
    search_fields = ['title', 'code']

    def get_queryset(self):
        return super().get_queryset().select_related('company')

    @swagger_auto_schema(
        operation_summary="Role List",
        operation_description="Get Role List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='role', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Role",
        operation_description="Create new role",
        request_body=RoleCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='role', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RoleDetail(BaseRetrieveMixin, BaseUpdateMixin, RoleDestroyMixin):
    permission_classes = [IsAuthenticated]
    queryset = Role.objects
    serializer_detail = RoleDetailSerializer
    serializer_update = RoleUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('employee', queryset=Employee.objects.select_related('group')),
        )

    @swagger_auto_schema(
        operation_summary="Role Detail",
        operation_description="Get Role Detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='role', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Role",
        operation_description="Update Role by ID",
        request_body=RoleUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='role', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Role",
        operation_description="Delete Role by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='role', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
