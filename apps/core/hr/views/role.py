from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.hr.mixins import RoleUpdateMixin, RoleRetrieveMixin, RoleCreateMixin, RoleListMixin, RoleDestroyMixin
from apps.core.hr.models import Role
from apps.core.hr.serializers.role_serializers import RoleUpdateSerializer, RoleDetailSerializer, RoleCreateSerializer, \
    RoleListSerializer


class RoleList(
    RoleListMixin,
    RoleCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Role.object_normal
    serializer_class = RoleListSerializer
    serializer_create = RoleCreateSerializer

    @swagger_auto_schema(
        operation_summary="Role List",
        operation_description="Get Role List",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Role",
        operation_description="Create new role",
        request_body=RoleCreateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RoleDetail(
    RoleRetrieveMixin,
    RoleUpdateMixin,
    RoleDestroyMixin,
    generics.GenericAPIView,
):
    permission_classes = [IsAuthenticated]
    queryset = Role.object_global
    serializer_class = RoleDetailSerializer
    serializer_update = RoleUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Role Detail",
        operation_description="Get Role Detail by ID",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Role",
        operation_description="Update Role by ID",
        request_body=RoleUpdateSerializer,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Role",
        operation_description="Delete Role by ID",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
