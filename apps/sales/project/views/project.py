__init__ = ['ProjectList', 'ProjectDetail', 'ProjectUpdate', 'ProjectMemberAdd', 'ProjectMemberDetail',
            'ProjectUpdateOrder', 'ProjectCreateBaseline', 'ProjectCreateBaseline', 'ProjectBaselineDetail']

from typing import Union

from django.conf import settings
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from apps.sales.project.models import Project, ProjectMapMember, ProjectBaseline
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, \
    BaseDestroyMixin, TypeCheck, ResponseController
from apps.sales.project.serializers import ProjectListSerializers, ProjectCreateSerializers, ProjectDetailSerializers, \
    ProjectUpdateSerializers, MemberOfProjectAddSerializer, MemberOfProjectDetailSerializer, \
    MemberOfProjectUpdateSerializer, ProjectUpdateOrderSerializers, ProjectCreateBaselineSerializers, \
    ProjectBaselineDetailSerializers, ProjectBaselineListSerializers
from ..extend_func import get_prj_mem_of_crt_user, check_permit_add_member_pj


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

    @classmethod
    def get_prj_allowed(cls, item_data):
        if item_data and isinstance(item_data, dict) and 'prj' in item_data and isinstance(item_data['prj'], dict):
            ids = list(item_data['prj'].keys())
            if TypeCheck.check_uuid_list(data=ids):
                return item_data['prj'].keys()
        return []

    def get_prj_has_view_this(self):
        return [
            str(item) for item in ProjectMapMember.objects.filter_current(
                fill__tenant=True, fill__company=True,
                member_id=self.cls_check.employee_attr.employee_current_id,
                permit_view_this_project=True,
            ).values_list('project_id', flat=True)
        ]

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:

        state_from_app, data_from_app = self.has_get_list_from_app()
        if state_from_app is True:
            if data_from_app and isinstance(data_from_app, list) and len(data_from_app) == 3:
                return self.filter_kwargs_q__from_app(data_from_app)
            return self.list_empty()
        # check permit config exists if from_app not calling...
        prj_has_view_ids = self.get_prj_has_view_this()
        if self.cls_check.permit_cls.config_data__exist or prj_has_view_ids:
            return self.filter_kwargs_q__from_config() | Q(id__in=prj_has_view_ids)
        return self.list_empty()

    def filter_kwargs_q__from_app(self, arr_from_app) -> Q:
        # permit_data = {"employee": [], "roles": []}
        prj_ids = []
        if arr_from_app and isinstance(arr_from_app, list) and len(arr_from_app) == 3:
            permit_data = self.cls_check.permit_cls.config_data__by_code(
                label_code=arr_from_app[0],
                model_code=arr_from_app[1],
                perm_code=arr_from_app[2],
                has_roles=False,
            )
            if 'employee' in permit_data:
                prj_ids += self.get_prj_allowed(item_data=permit_data['employee'])
            if 'roles' in permit_data and isinstance(permit_data['roles'], list):
                for item_data in permit_data['roles']:
                    prj_ids += self.get_prj_allowed(item_data=item_data)
            if settings.DEBUG_PERMIT:
                print('=> prj_ids:                :', '[HAS FROM APP]', prj_ids)
        return Q(id__in=list(set(prj_ids)))

    @swagger_auto_schema(
        operation_summary="Project list",
        operation_description="get project list",
    )
    @mask_view(
        login_require=True, auth_require=True,
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
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        prj_obj = instance
        if emp_id and str(prj_obj.employee_inherit_id) == str(emp_id):
            return True
        obj_of_current_user = get_prj_mem_of_crt_user(
            prj_obj=prj_obj, employee_current=self.cls_check.employee_attr.employee_current
        )
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
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
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class ProjectMemberAdd(BaseCreateMixin):
    queryset = ProjectMapMember  # noqa
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
            self.ser_context = {
                'project_id': str(pj_obj.id),
            }
            if self.check_permit_add_member_pj(project_obj=pj_obj):
                setattr(self, 'project_id', str(pj_obj.id))
                return self.create(request, *args, pk_pj, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class ProjectMemberDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProjectMapMember.objects
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

    def manual_check_obj_retrieve(self, instance, **kwargs):
        state = self.check_has_permit_of_space_all(pj_obj=instance.project)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
                return True
            obj_of_current_user = get_prj_mem_of_crt_user(
                instance.project, self.cls_check.employee_attr.employee_current
            )
            if obj_of_current_user:
                return obj_of_current_user.permit_view_this_project
        return state

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
            return True

        obj_of_current_user = get_prj_mem_of_crt_user(
            instance.project, self.cls_check.employee_attr.employee_current
        )
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

        obj_of_current_user = get_prj_mem_of_crt_user(
            instance.project, self.cls_check.employee_attr.employee_current
        )
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


class ProjectUpdateOrder(BaseUpdateMixin):
    queryset = Project.objects
    serializer_update = ProjectUpdateOrderSerializers
    retrieve_hidden_field = ('tenant_id', 'company_id')

    def get_project_member_of_current_user(self, instance):
        return ProjectMapMember.objects.filter_current(
            project=instance,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(instance.employee_inherit_id) == str(emp_id):
            return True

        obj_of_current_user = self.get_project_member_of_current_user(instance=instance)
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    @swagger_auto_schema(
        operation_summary='Update order',
        operation_description='Update order group and work',
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, pk, **kwargs):
        if TypeCheck.check_uuid(pk):
            return self.update(request, *args, pk, **kwargs)
        return ResponseController.notfound_404()


class ProjectCreateBaseline(BaseListMixin, BaseCreateMixin):
    queryset = ProjectBaseline.objects
    serializer_list = ProjectBaselineListSerializers
    serializer_create = ProjectCreateBaselineSerializers
    serializer_detail = ProjectBaselineDetailSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]

    @swagger_auto_schema(
        operation_summary="Project baseline list",
        operation_description="get project baseline list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='project', model_code='project', perm_code='view',
        skip_filter_employee=True
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create project baseline",
        operation_description="Create baseline of project",
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        pj_obj = get_project_obj(request.data.get('project'))
        emp_obj = self.cls_check.employee_attr.employee_current
        if pj_obj:
            self.ser_context = {
                'project_id': str(pj_obj.id)
            }
            if check_permit_add_member_pj(task=pj_obj, emp_crt=emp_obj):
                setattr(self, 'project_id', str(pj_obj.id))
                return self.create(request, *args, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class ProjectBaselineDetail(BaseRetrieveMixin):
    queryset = ProjectBaseline.objects
    serializer_detail = ProjectBaselineDetailSerializers
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

    def manual_check_obj_retrieve(self, instance, **kwargs):
        state = self.check_has_permit_of_space_all(pj_obj=instance.project)
        if not state:
            # special case skip with True if current user is employee_inherit
            emp_id = self.cls_check.employee_attr.employee_current_id
            if emp_id and str(instance.project.employee_inherit_id) == str(emp_id):
                return True
            obj_of_current_user = get_prj_mem_of_crt_user(
                instance.project, self.cls_check.employee_attr.employee_current
            )
            if obj_of_current_user:
                return obj_of_current_user.permit_view_this_project
        return state

    @swagger_auto_schema(
        operation_summary='Get member detail of Project',
        operation_description='Get member detail of Project related',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="view",
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)
