__all__ = ['ProjectWorkList', 'ProjectWorkDetail']

from typing import Union

from django.conf import settings
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from apps.sales.project.extend_func import get_prj_mem_of_crt_user
from apps.sales.project.models import ProjectWorks, ProjectMapMember, Project
from apps.sales.project.serializers import WorkListSerializers, WorkCreateSerializers, WorkDetailSerializers, \
    WorkUpdateSerializers
from apps.shared import BaseListMixin, BaseCreateMixin, mask_view, TypeCheck, ResponseController, BaseRetrieveMixin, \
    BaseUpdateMixin, BaseDestroyMixin


# common function
def get_project_obj(pk_idx):
    if TypeCheck.check_uuid(pk_idx):
        return Project.objects.filter_current(pk=pk_idx, fill__tenant=True, fill__company=True).first()
    return None


class ProjectWorkList(BaseListMixin, BaseCreateMixin):
    queryset = ProjectWorks.objects
    serializer_list = WorkListSerializers
    serializer_create = WorkCreateSerializers
    serializer_detail = WorkDetailSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = [
        'tenant_id', 'company_id',
        'employee_created_id',
    ]
    filterset_fields = {
        'employee_inherit': ['exact', 'in'],
    }

    @classmethod
    def get_prj_allowed(cls, item_data):
        if item_data and isinstance(item_data, dict) and 'prj' in item_data and isinstance(item_data['prj'], dict):
            ids = list(item_data['prj'].keys())
            if TypeCheck.check_uuid_list(data=ids):
                return item_data['prj'].keys()
        return []

    def get_project_has_view_this(self):
        return [
            str(item) for item in ProjectMapMember.objects.filter_current(
                fill__tenant=True, fill__company=True,
                member_id=self.cls_check.employee_attr.employee_current_id,
                permit_view_this_project=True,
            ).values_list('project_id', flat=True)
        ]

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        """
        Check case get list opp for feature or list by configured.
        query_params: from_app=app_label-model_code
        """
        state_from_app, data_from_app = self.has_get_list_from_app()
        if state_from_app is True:
            if data_from_app and isinstance(data_from_app, list) and len(data_from_app) == 3:
                return self.filter_kwargs_q__from_app(data_from_app)
            return self.list_empty()
        # check permit config exists if from_app not calling...
        project_has_view_ids = self.get_project_has_view_this()
        if self.cls_check.permit_cls.config_data__exist or project_has_view_ids:
            return self.filter_kwargs_q__from_config() | Q(id__in=project_has_view_ids)
        return self.list_empty()

    def filter_kwargs_q__from_app(self, arr_from_app) -> Q:
        # permit_data = {"employee": [], "roles": []}
        project_ids = []
        if arr_from_app and isinstance(arr_from_app, list) and len(arr_from_app) == 3:
            permit_data = self.cls_check.permit_cls.config_data__by_code(
                label_code=arr_from_app[0],
                model_code=arr_from_app[1],
                perm_code=arr_from_app[2],
                has_roles=False,
            )
            if 'employee' in permit_data:
                project_ids += self.get_prj_allowed(item_data=permit_data['employee'])
            if 'roles' in permit_data and isinstance(permit_data['roles'], list):
                for item_data in permit_data['roles']:
                    project_ids += self.get_prj_allowed(item_data=item_data)
            if settings.DEBUG_PERMIT:
                print('=> project_ids:                :', '[HAS FROM APP]', project_ids)
        return Q(id__in=list(set(project_ids)))

    @swagger_auto_schema(
        operation_summary="Project work list",
        operation_description="get project work list",
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
        operation_summary="Create project work",
        operation_description="Create project work",
        request_body=WorkCreateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code='create'
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        prj_pk = data.get('project')
        pj_obj = get_project_obj(prj_pk)
        if pj_obj:
            if self.check_permit_add_gaw(project_obj=pj_obj):
                return self.create(request, *args, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class ProjectWorkDetail(BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin):
    queryset = ProjectWorks.objects
    serializer_detail = WorkDetailSerializers
    serializer_update = WorkUpdateSerializers
    retrieve_hidden_field = ('tenant_id', 'company_id')

    def get_queryset(self):
        return super().get_queryset().select_related('work_dependencies_parent')

    def check_has_permit_of_space_all(self, opp_obj):  # pylint: disable=R0912
        config_data = self.cls_check.permit_cls.config_data  # noqa
        if config_data and isinstance(config_data, dict):  # pylint: disable=R1702
            if 'employee' in config_data and isinstance(config_data['employee'], dict):
                if 'general' in config_data['employee']:
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

    def manual_check_obj_update(self, instance, body_data, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        project_map_work = instance.project_projectmapwork_work.all().first()
        if emp_id and str(project_map_work.project.employee_inherit_id) == str(emp_id):
            return True
        obj_of_current_user = get_prj_mem_of_crt_user(
            instance.project_projectmapwork_work.all().first().project, self.cls_check.employee_attr.employee_current
        )
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    def manual_check_obj_destroy(self, instance, **kwargs):
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        prj = instance.project_projectmapwork_work.all().first().project
        emp = str(prj.employee_inherit_id)

        if str(emp_id) == emp:
            # owner auto allow in member
            return True

        obj_of_current_user = get_prj_mem_of_crt_user(
            instance.project_projectmapwork_work.all().first().project, self.cls_check.employee_attr.employee_current
        )
        if obj_of_current_user:
            return obj_of_current_user.permit_add_gaw
        return False

    @swagger_auto_schema(
        operation_summary='Get work detail',
        operation_description='Get work detail by ID',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="view",
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update work for project',
        operation_description='Update work detail by ID',
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
        operation_summary='Remove work from project'
    )
    @mask_view(login_require=True, auth_require=False)
    def delete(self, request, *args, pk, **kwargs):
        return self.destroy(request, *args, pk, **kwargs)
