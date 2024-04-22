__all__ = ['ProjectGroupList', 'ProjectGroupDetail']

from drf_yasg.utils import swagger_auto_schema

from apps.sales.project.models import ProjectGroups, ProjectMapMember, Project
from apps.sales.project.serializers import GroupListSerializers, GroupCreateSerializers, GroupDetailSerializers
from apps.shared import BaseListMixin, mask_view, TypeCheck, ResponseController, BaseRetrieveMixin, BaseUpdateMixin, \
    BaseDestroyMixin, BaseCreateMixin


def get_project_obj(pk_idx):
    if TypeCheck.check_uuid(pk_idx):
        return Project.objects.filter_current(pk=pk_idx, fill__tenant=True, fill__company=True).first()
    return None


class ProjectGroupList(BaseListMixin, BaseCreateMixin):
    queryset = ProjectGroups.objects
    serializer_list = GroupListSerializers
    serializer_create = GroupCreateSerializers
    serializer_detail = GroupDetailSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = ['title']
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    # filterset_class = ProjectGroupListFilter

    @swagger_auto_schema(
        operation_summary="Project group list",
        operation_description="get project group list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_project_member_of_current_user(self, project_obj):
        return ProjectMapMember.objects.filter_current(
            project=project_obj,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def check_permit_add_gaw(self, project_obj) -> bool:
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(project_obj.employee_inherit_id) == str(emp_id):
            return True

        project_member_current_user = self.get_project_member_of_current_user(project_obj=project_obj)
        if project_member_current_user:
            return project_member_current_user.permit_add_gaw
        return False

    @swagger_auto_schema(
        operation_summary="Create project group",
        operation_description="Create project group",
        request_body=GroupCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='project', model_code='project', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        pk = data.get('project')
        pj_obj = get_project_obj(pk)
        if pj_obj:
            if self.check_permit_add_gaw(project_obj=pj_obj):
                return self.create(request, *args, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class ProjectGroupDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProjectGroups.objects
    serializer_detail = GroupDetailSerializers
    serializer_update = GroupDetailSerializers
    retrieve_hidden_field = ('tenant_id', 'company_id')

    def check_has_permit_of_space_all(self, pj_obj):
        config_data = self.cls_check.permit_cls.config_data  # noqa
        if config_data and isinstance(config_data, dict):
            if 'employee' in config_data and isinstance(config_data['employee'], dict):
                if 'general' in config_data['employee']:  # fix bug keyError: 'general'
                    general_data = config_data['employee']['general']
                    if general_data and isinstance(general_data, dict):
                        for _permit_code, permit_config in general_data.items():
                            if permit_config and isinstance(permit_config, dict) and 'space' in permit_config:
                                if (
                                        permit_config['space'] == '1'
                                        and str(pj_obj.company_id) == self.cls_check.employee_attr.company_id
                                ):
                                    return True
            if 'roles' in config_data and isinstance(config_data['roles'], list):
                for role_data in config_data['roles']:
                    general_data = role_data['general']
                    if general_data and isinstance(general_data, dict):
                        for _permit_code, permit_config in general_data.items():
                            if permit_config and isinstance(permit_config, dict) and 'space' in permit_config:
                                if (
                                        permit_config['space'] == '1'
                                        and str(pj_obj.company_id) == self.cls_check.employee_attr.company_id
                                ):
                                    return True
        return False

    def get_project_member_of_current_user(self, instance):
        project = instance.project_projectmapgroup_group.all().first().project
        return ProjectMapMember.objects.filter_current(
            project=project,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        project_map_group = instance.project_projectmapgroup_group.all().first()
        if emp_id and str(project_map_group.project.employee_inherit_id) == str(emp_id):
            return True
        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    def manual_check_obj_destroy(self, instance, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        project_map_group = instance.project_projectmapgroup_group.all().first()
        if emp_id and str(project_map_group.project.employee_inherit_id) == str(emp_id):
            # owner auto allow in member
            return True
        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    @swagger_auto_schema(
        operation_summary='Get group detail',
        operation_description='Get group detail by ID',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="view",
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update group detail',
        operation_description='Update group detail by ID',
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk, **kwargs):
        data = request.data
        project_id = data.get('project', None)
        employee_id = data.get('employee_inherit', None) if data.get(
            'employee_inherit', None
        ) is not None else request.user.employee_current_id
        if TypeCheck.check_uuid(project_id) and TypeCheck.check_uuid(employee_id):
            return self.update(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Remove group from project',
        operation_description='Remove group detail by ID',
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, is_purge=True, **kwargs)
