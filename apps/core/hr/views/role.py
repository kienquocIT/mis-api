from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.hr.mixins import RoleCreateMixin, RoleDestroyMixin
from apps.core.hr.models import Role
from apps.core.hr.serializers.role_serializers import RoleUpdateSerializer, RoleDetailSerializer, RoleCreateSerializer,\
    RoleListSerializer
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseUpdateMixin, BaseDestroyMixin, BaseRetrieveMixin


class RoleList(
    BaseListMixin,
    RoleCreateMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Role.object_global.select_related("company")
    serializer_list = RoleListSerializer
    serializer_create = RoleCreateSerializer
    serializer_detail = RoleDetailSerializer

    @swagger_auto_schema(
        operation_summary="Role List",
        operation_description="Get Role List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Role",
        operation_description="Create new role",
        request_body=RoleCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RoleDetail(
    BaseRetrieveMixin,
    BaseUpdateMixin,
    RoleDestroyMixin,
):
    permission_classes = [IsAuthenticated]
    queryset = Role.object_global
    serializer_detail = RoleDetailSerializer
    serializer_update = RoleUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Role Detail",
        operation_description="Get Role Detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Role",
        operation_description="Update Role by ID",
        request_body=RoleUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        self.serializer_class = RoleUpdateSerializer
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Role",
        operation_description="Delete Role by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
