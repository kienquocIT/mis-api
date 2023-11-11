from typing import Union

from django.db.models import Prefetch, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.response import Response

from apps.core.hr.mixins import RoleDestroyMixin
from apps.core.hr.models import Role, Employee, PlanRoleApp
from apps.core.hr.serializers.role_serializers import (
    RoleUpdateSerializer, RoleDetailSerializer,
    RoleCreateSerializer,
    RoleListSerializer, ApplicationOfRoleSerializer,
)
from apps.shared import mask_view, BaseListMixin, BaseUpdateMixin, BaseRetrieveMixin, BaseCreateMixin


class RoleList(BaseListMixin, BaseCreateMixin):
    queryset = Role.objects
    serializer_list = RoleListSerializer
    serializer_create = RoleCreateSerializer
    serializer_detail = RoleDetailSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    search_fields = ['title', 'code']

    def get_queryset(self):
        return super().get_queryset().select_related('company')

    @swagger_auto_schema(
        operation_summary="Role List",
        operation_description="Get Role List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='view',
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
        allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RoleDetail(BaseRetrieveMixin, BaseUpdateMixin, RoleDestroyMixin):
    queryset = Role.objects
    serializer_detail = RoleDetailSerializer
    serializer_update = RoleUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

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
        allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='view',
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
        allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Role",
        operation_description="Delete Role by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RoleAppList(BaseListMixin):
    queryset = PlanRoleApp.objects
    search_fields = ["application__title"]
    serializer_list = ApplicationOfRoleSerializer

    @property
    def filter_kwargs(self) -> dict[str, any]:
        return {
            'plan_role__role_id': self.kwargs['pk'],
        }

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        role_id = self.kwargs['pk']
        try:
            role_obj = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            raise exceptions.NotFound

        state = self.check_perm_by_obj_or_body_data(obj=role_obj, auto_check=True)
        if state is True:
            return Q()
        return self.list_empty()

    @swagger_auto_schema(
        operation_summary="Application List of Employee",
        operation_description="Application List of Employee",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='role', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.list(request, *args, pk, **kwargs)
