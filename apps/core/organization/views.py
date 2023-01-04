from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.organization.mixins import OrganizationListMixin, OrganizationCreateMixin, OrganizationRetrieveMixin, \
    OrganizationUpdateMixin, RoleListMixin, RoleCreateMixin, RoleRetrieveMixin, RoleUpdateMixin
from apps.core.organization.models import GroupLevel, Group
from apps.core.hr.models import Role, RoleHolder
from apps.core.organization.serializers import GroupLevelListSerializer, GroupLevelCreateSerializer, \
    GroupListSerializer, GroupCreateSerializer, GroupLevelDetailSerializer, GroupLevelUpdateSerializer, \
    GroupUpdateSerializer, GroupDetailSerializer, GroupLevelMainCreateSerializer, RoleListSerializer, \
    RoleCreateSerializer, RoleUpdateSerializer, RoleDetailSerializer
from apps.shared import ResponseController


# Group Level
class GroupLevelList(
    OrganizationListMixin,
    OrganizationCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = GroupLevel.object_global
    search_fields = [
        "description",
        "first_manager_description",
        "second_manager_description"
    ]

    serializer_class = GroupLevelListSerializer
    serializer_create = GroupLevelMainCreateSerializer

    @swagger_auto_schema(
        operation_summary="Group Level list",
        operation_description="Get group level list",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Group Level",
        operation_description="Create new group level",
        request_body=GroupLevelMainCreateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupLevelDetail(
    OrganizationRetrieveMixin,
    OrganizationUpdateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = GroupLevel.object_global
    serializer_class = GroupLevelDetailSerializer
    serializer_update = GroupLevelUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Group Level detail",
        operation_description="Get Group level detail by ID",
    )
    def get(self, request, *args, **kwargs):
        self.serializer_class = GroupLevelDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Group Level",
        operation_description="Update Group Level by ID",
        request_body=GroupLevelUpdateSerializer,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Group
class GroupList(
    OrganizationListMixin,
    OrganizationCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Group.object_global.select_related(
        "group_level",
        "first_manager",
        "parent_n",
    )
    search_fields = [
        "title",
        "code",
        "description",
        "first_manager_title",
        "second_manager_title"
    ]

    serializer_class = GroupListSerializer
    serializer_create = GroupCreateSerializer

    @swagger_auto_schema(
        operation_summary="Group list",
        operation_description="Get group list",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Group",
        operation_description="Create new group",
        request_body=GroupCreateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupDetail(
    OrganizationRetrieveMixin,
    OrganizationUpdateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Group.object_global
    serializer_class = GroupDetailSerializer
    serializer_update = GroupUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Group detail",
        operation_description="Get Group detail by ID",
    )
    def get(self, request, *args, **kwargs):
        self.serializer_class = GroupDetailSerializer
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Group",
        operation_description="Update Group by ID",
        request_body=GroupUpdateSerializer,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Group",
        operation_description="Delete Group by ID",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class RoleList(
    RoleListMixin,
    RoleCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
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
    generics.GenericAPIView
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

    @swagger_auto_schema(operation_summary="Delete Role")
    def delete(self, request, pk, *args, **kwargs):
        try:
            role = Role.objects.get(pk=pk)
            role_holder = RoleHolder.object_normal.filter(role_id=pk)
            role_holder.delete()
            role.delete()
            return ResponseController.success_200({'detail': 'success'}, key_data='result')
        except:
            return ResponseController.bad_request_400(msg='User does not exist')
<<<<<<< .mine
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
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
    generics.GenericAPIView
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

    @swagger_auto_schema(operation_summary="Delete Role")
    def delete(self, request, pk, *args, **kwargs):
        try:
            role = Role.objects.get(pk=pk)
            role_holder = RoleHolder.object_normal.filter(role_id=pk)
            role_holder.delete()
            role.delete()
            return ResponseController.success_200({'detail': 'success'}, key_data='result')
        except:
            return ResponseController.bad_request_400(msg='User does not exist')
=======

























































>>>>>>> .theirs
