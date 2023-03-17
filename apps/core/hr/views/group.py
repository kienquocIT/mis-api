from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.mixins import HRListMixin, HRDestroyMixin
from apps.core.hr.models import GroupLevel, Group
from apps.core.hr.serializers.group_serializers import (
    GroupLevelListSerializer,
    GroupListSerializer, GroupCreateSerializer, GroupLevelDetailSerializer, GroupLevelUpdateSerializer,
    GroupUpdateSerializer, GroupDetailSerializer, GroupLevelMainCreateSerializer, GroupParentListSerializer,
)
from apps.shared import BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Group Level
class GroupLevelList(
    BaseListMixin,
    BaseCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = GroupLevel.objects
    search_fields = [
        "description",
        "first_manager_description",
        "second_manager_description"
    ]

    serializer_list = GroupLevelListSerializer
    serializer_detail = GroupLevelListSerializer
    serializer_create = GroupLevelMainCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'user_created']
    use_cache_queryset = True

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
    BaseRetrieveMixin,
    BaseUpdateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = GroupLevel.objects
    serializer_detail = GroupLevelDetailSerializer
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
    BaseListMixin,
    BaseCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects
    search_fields = [
        "title",
        "code",
        "description",
        "first_manager_title",
        "second_manager_title"
    ]
    ordering = ['group_level__level']

    serializer_list = GroupListSerializer
    serializer_detail = GroupListSerializer
    serializer_create = GroupCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'user_created']

    def get_queryset(self):
        return super().get_queryset().select_related(
            "group_level",
            "first_manager",
            "parent_n",
        ).filter(is_delete=False)

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
    BaseRetrieveMixin,
    BaseUpdateMixin,
    HRDestroyMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects
    serializer_detail = GroupDetailSerializer
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


class GroupParentList(
    HRListMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects
    search_fields = []
    ordering = ['group_level__level']

    serializer_list = GroupParentListSerializer

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    @swagger_auto_schema(
        operation_summary="Group parent list",
        operation_description="Get group parent list",
    )
    def get(self, request, *args, **kwargs):
        return self.list_group_parent(request, **kwargs)
