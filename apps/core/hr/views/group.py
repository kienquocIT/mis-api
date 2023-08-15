from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.core.hr.mixins import HRDestroyMixin
from apps.core.hr.models import GroupLevel, Group
from apps.core.hr.serializers.group_serializers import (
    GroupLevelListSerializer,
    GroupListSerializer, GroupCreateSerializer, GroupLevelDetailSerializer, GroupLevelUpdateSerializer,
    GroupUpdateSerializer, GroupDetailSerializer, GroupParentListSerializer, GroupLevelCreateSerializer,
)
from apps.shared import BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, mask_view


# Group Level
class GroupLevelList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = GroupLevel.objects
    search_fields = [
        "description",
        "first_manager_description",
        "second_manager_description"
    ]

    serializer_list = GroupLevelListSerializer
    serializer_detail = GroupLevelListSerializer
    serializer_create = GroupLevelCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id']
    use_cache_queryset = True

    def error_auth_require(self):
        return self.list_empty()

    @swagger_auto_schema(
        operation_summary="Group Level list",
        operation_description="Get group level list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Group Level",
        operation_description="Create new group level",
        request_body=GroupLevelCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupLevelDetail(BaseRetrieveMixin, BaseUpdateMixin):
    permission_classes = [IsAuthenticated]
    queryset = GroupLevel.objects
    serializer_detail = GroupLevelDetailSerializer
    serializer_update = GroupLevelUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Group Level detail",
        operation_description="Get Group level detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Group Level",
        operation_description="Update Group Level by ID",
        request_body=GroupLevelUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# Group
class GroupList(BaseListMixin, BaseCreateMixin):
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
    create_hidden_field = ['tenant_id', 'company_id']

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
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='view'
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Group",
        operation_description="Create new group",
        request_body=GroupCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupDetail(BaseRetrieveMixin, BaseUpdateMixin, HRDestroyMixin):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects
    serializer_detail = GroupDetailSerializer
    serializer_update = GroupUpdateSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema(
        operation_summary="Group detail",
        operation_description="Get Group detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Group",
        operation_description="Update Group by ID",
        request_body=GroupUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Group",
        operation_description="Delete Group by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='delete',
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GroupParentList(BaseListMixin):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects
    search_fields = []
    ordering = ['group_level__level']

    serializer_list = GroupParentListSerializer
    serializer_detail = GroupParentListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)

    def setup_list_field_hidden(self, user, **kwargs):
        data = super().setup_list_field_hidden(user)
        if 'level' in self.kwargs:
            level = int(self.kwargs['level'])
            del self.kwargs['level']
            data['group_level__level__lt'] = level
        return data

    def error_auth_require(self):
        return self.list_empty()

    @swagger_auto_schema(
        operation_summary="Group parent list",
        operation_description="Get group parent list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        plan_code='base', app_code='group', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        if 'level' in kwargs:
            del kwargs['level']
        return self.list(request, **kwargs)
