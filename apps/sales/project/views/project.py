__init__ = ['ProjectList', 'ProjectDetail', 'ProjectUpdate', 'ProjectMemberAdd', 'ProjectMemberDetail',
            'ProjectGroupList', 'ProjectGroupDetail']

from typing import Union

from drf_yasg.utils import swagger_auto_schema

from apps.sales.project.filters import ProjectGroupListFilter
from apps.sales.project.models import Project, ProjectMapMember, ProjectGroups
from apps.sales.project.serializers import ProjectListSerializers, ProjectCreateSerializers, ProjectDetailSerializers, \
    ProjectUpdateSerializers, MemberOfProjectAddSerializer, MemberOfProjectDetailSerializer, \
    MemberOfProjectUpdateSerializer, GroupListSerializers, GroupCreateSerializers, GroupDetailSerializers
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin, \
    TypeCheck, ResponseController


# common function
def get_project_obj(pk_idx):
    if TypeCheck.check_uuid(pk_idx):
        return Project.objects.filter_current(pk=pk_idx, fill__tenant=True, fill__company=True).first()
    return None


class ProjectList(BaseListMixin, BaseCreateMixin):
    queryset = Project.objects
    serializer_list = ProjectListSerializers
    serializer_create = ProjectCreateSerializers
    serializer_detail = ProjectDetailSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    search_fields = ['title', 'code']
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    # def get_queryset(self):
    #     return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="Project list",
        operation_description="get project list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create project",
        operation_description="Create project",
        request_body=ProjectCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='project', model_code='project', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ProjectDetail(BaseRetrieveMixin):
    queryset = Project.objects
    serializer_detail = ProjectDetailSerializers
    retrieve_hidden_field = ('tenant_id', 'company_id')

    def get_queryset(self):
        return super().get_queryset().prefetch_related("members", )

    def manual_check_obj_retrieve(self, instance, **kwargs) -> Union[None, bool]:  # pylint: disable=R0911,R0912
        # This function automatically runs when a user using the put method
        self.ser_context = {  # noqa
            'allow_get_member': False,
        }

        # owner
        if str(instance.employee_inherit_id) == str(self.cls_check.employee_attr.employee_current_id):
            self.ser_context['allow_get_member'] = True

        # is member
        pj_member = ProjectMapMember.objects.filter_current(
            fill__tenant=True, fill__company=True,
            project=instance,
            member_id=self.cls_check.employee_attr.employee_current_id,
        )
        if pj_member.exists():  # noqa
            self.ser_context['allow_get_member'] = True
            return True

        # has view project with space all
        config_data = self.cls_check.permit_cls.config_data
        if config_data and isinstance(config_data, dict):  # pylint: disable=R1702
            range_has_space_1 = []

            employee_data = self.cls_check.permit_cls.config_data.get('employee', {})
            if employee_data and isinstance(employee_data, dict) and 'general' in employee_data:
                general_data = employee_data.get('general', {})
                if general_data and isinstance(general_data, dict):
                    for permit_range, permit_config in general_data.items():
                        if (
                                isinstance(permit_config, dict)
                                and permit_config
                                and 'space' in permit_config
                                and permit_config['space'] == '1'
                        ):
                            range_has_space_1.append(permit_range)

            roles_data = self.cls_check.permit_cls.config_data.get('roles', [])
            if roles_data and isinstance(roles_data, list):
                for role_detail in roles_data:
                    general_data = role_detail.get('general', {}) if isinstance(role_detail, dict) else {}
                    if general_data and isinstance(general_data, dict):
                        for permit_range, permit_config in general_data.items():
                            if (
                                    isinstance(permit_config, dict)
                                    and permit_config
                                    and 'space' in permit_config
                                    and permit_config['space'] == '1'
                            ):
                                range_has_space_1.append(permit_range)

            if range_has_space_1:
                self.ser_context['allow_get_member'] = True
                try:
                    pj_inherit_id = str(instance.employee_inherit_id)
                    if '1' in range_has_space_1:
                        if str(self.cls_check.employee_attr.employee_current_id) == pj_inherit_id:
                            return True

                    if '2' in range_has_space_1:
                        if pj_inherit_id in self.cls_check.employee_attr.employee_staff_ids__exclude_me():
                            return True

                    if '3' in range_has_space_1:
                        if pj_inherit_id in self.cls_check.employee_attr.employee_same_group_ids__exclude_me():
                            return True

                    if '4' in range_has_space_1:
                        if str(instance.company_id) == str(self.cls_check.employee_attr.company_id):
                            return True
                except ValueError:
                    return False

        return False

    @swagger_auto_schema(
        operation_summary='Project detail',
        operation_description='Get detail of Project',
    )
    @mask_view(
        login_require=True, auth_require=False, employee_required=True,
        label_code='project', model_code='project', perm_code="view",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ProjectUpdate(BaseUpdateMixin, BaseDestroyMixin):
    queryset = Project.objects
    serializer_update = ProjectUpdateSerializers
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "members",
        )

    def manual_check_obj_update(self, instance, body_data, **kwargs) -> Union[None, bool]:
        # This function automatically runs when a user using the put method
        if str(instance.employee_inherit_id) == str(self.cls_check.employee_attr.employee_current_id):
            return True
        return False

    @swagger_auto_schema(
        operation_summary="Update Project",
        operation_description="Update Project by ID",
        request_body=ProjectUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="edit",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ProjectMemberAdd(BaseCreateMixin):
    queryset = ProjectMapMember # noqa
    serializer_create = MemberOfProjectAddSerializer

    def get_project_member_of_current_user(self, project_obj):
        return ProjectMapMember.objects.filter_current(
            project=project_obj,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def check_permit_add_member_pj(self, project_obj) -> bool:
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(project_obj.employee_inherit_id) == str(emp_id):
            return True

        project_member_current_user = self.get_project_member_of_current_user(project_obj=project_obj)
        if project_member_current_user:
            return project_member_current_user.permit_add_member
        return False

    def create_hidden_field_manual_after(self):
        return {
            'tenant_id': self.cls_check.employee_attr.tenant_id,
            'company_id': self.cls_check.employee_attr.company_id,
            'project_id': getattr(self, 'project_id', None),
        }

    def get_serializer_detail_return(self, obj):
        return {'member': 'Successful'}

    @swagger_auto_schema(
        operation_summary="Add member project",
        operation_description="Add member project",
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, pk_pj, **kwargs):
        pj_obj = get_project_obj(pk_pj)
        if pj_obj:
            if self.check_permit_add_member_pj(project_obj=pj_obj):
                setattr(self, 'project_id', pj_obj.id)
                return self.create(request, *args, pk_pj, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class ProjectMemberDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProjectMapMember.objects # noqa
    serializer_detail = MemberOfProjectDetailSerializer
    serializer_update = MemberOfProjectUpdateSerializer

    retrieve_hidden_field = ('tenant_id', 'company_id')

    def check_has_permit_of_space_all(self, pj_obj):  # pylint: disable=R0912
        config_data = self.cls_check.permit_cls.config_data  # noqa
        if config_data and isinstance(config_data, dict):  # pylint: disable=R1702
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
        return ProjectMapMember.objects.filter_current(
            project=instance.project,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def manual_check_obj_retrieve(self, instance, **kwargs):
        state = self.check_has_permit_of_space_all(pj_obj=instance.project)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
                return True
            obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
            if obj_of_current_user:
                return obj_of_current_user.permit_view_this_project
        return state

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
            return True

        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_member
        return False

    def manual_check_obj_destroy(self, instance, **kwargs):
        if instance.member_id == instance.project.employee_inherit_id:
            return False

        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id

        if emp_id == instance.member_id:
            # deny delete member is owner opp.
            return False

        if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
            # owner auto allow in member
            return True

        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_view_this_project
        return False

    def get_lookup_url_kwarg(self) -> dict:
        return {
            'project_id': self.kwargs['pk_pj'],
            'member_id': self.kwargs['pk_member']
        }

    @swagger_auto_schema(
        operation_summary='Get member detail of Project',
        operation_description='Get member detail of Project related',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="view",
    )
    def get(self, request, *args, pk_pj, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_pj) and TypeCheck.check_uuid(pk_member):
            return self.retrieve(request, *args, pk_pj, pk_member, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Update app and permit for member',
        operation_description='Update app and permit for member',
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk_pj, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_pj) and TypeCheck.check_uuid(pk_member):
            return self.update(request, *args, pk_pj, pk_member, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Remove member from project'
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, pk_pj, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_pj) and TypeCheck.check_uuid(pk_member):
            return self.destroy(request, *args, pk_pj, pk_member, is_purge=True, **kwargs)
        return ResponseController.notfound_404()


class ProjectGroupList(BaseListMixin, BaseCreateMixin): # noqa
    queryset = ProjectGroups.objects
    serializer_list = GroupListSerializers
    serializer_create = GroupCreateSerializers
    serializer_detail = GroupDetailSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
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
    queryset = ProjectGroups.objects # noqa
    serializer_detail = GroupDetailSerializers
    serializer_update = GroupDetailSerializers

    retrieve_hidden_field = ('tenant_id', 'company_id')

    def check_has_permit_of_space_all(self, opp_obj):  # pylint: disable=R0912
        config_data = self.cls_check.permit_cls.config_data # noqa
        if config_data and isinstance(config_data, dict):  # pylint: disable=R1702
            if 'employee' in config_data and isinstance(config_data['employee'], dict):
                if 'general' in config_data['employee']:  # fix bug keyError: 'general'
                    general_data = config_data['employee']['general']
                    if general_data and isinstance(general_data, dict):
                        for _permit_code, permit_config in general_data.items():
                            if permit_config and isinstance(permit_config, dict) and 'space' in permit_config:
                                if (
                                        permit_config['space'] == '1'
                                        and str(opp_obj.company_id) == self.cls_check.employee_attr.company_id
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
                                        and str(opp_obj.company_id) == self.cls_check.employee_attr.company_id
                                ):
                                    return True
        return False

    def get_project_member_of_current_user(self, instance):
        return ProjectMapMember.objects.filter_current(
            project=instance.project,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def manual_check_obj_retrieve(self, instance, **kwargs):
        state = self.check_has_permit_of_space_all(opp_obj=instance.project)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.opportunity.employee_inherit_id) == str(emp_id):
                return True

            obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
            if obj_of_current_user:
                return obj_of_current_user.permit_add_gaw
        return state

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
            return True
        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    def manual_check_obj_destroy(self, instance, **kwargs):
        if instance.member_id == instance.project.employee_inherit_id:
            return False

        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id

        if emp_id == instance.member_id:
            # deny delete member is owner opp.
            return False

        if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
            # owner auto allow in member
            return True

        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    def get_lookup_url_kwarg(self) -> dict:
        return {
            'project_id': self.kwargs['pk_opp'],
            'member_id': self.kwargs['pk_member']
        }

    @swagger_auto_schema(
        operation_summary='Get group detail',
        operation_description='Get group detail by ID',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='opportunity', model_code='opportunity', perm_code="view",
    )
    def get(self, request, *args, pk_pj, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_pj) and TypeCheck.check_uuid(pk_member):
            return self.retrieve(request, *args, pk_pj, pk_member, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Update app and permit for member',
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk_opp, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_opp) and TypeCheck.check_uuid(pk_member):
            return self.update(request, *args, pk_opp, pk_member, **kwargs)
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary='Remove member from opp'
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, pk_opp, pk_member, **kwargs):
        if TypeCheck.check_uuid(pk_opp) and TypeCheck.check_uuid(pk_member):
            return self.destroy(request, *args, pk_opp, pk_member, is_purge=True, **kwargs)
        return ResponseController.notfound_404()
