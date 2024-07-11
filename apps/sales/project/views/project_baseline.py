__all__ = ['ProjectCreateBaseline', 'ProjectBaselineDetail', 'ProjectBaselineUpdate']

from typing import Union

from drf_yasg.utils import swagger_auto_schema

from apps.shared import BaseCreateMixin, BaseListMixin, BaseRetrieveMixin, mask_view, ResponseController, TypeCheck, \
    BaseUpdateMixin
from ..extend_func import check_permit_add_member_pj, get_prj_mem_of_crt_user
from ..models import ProjectBaseline, Project
from ..serializers import ProjectBaselineListSerializers, ProjectCreateBaselineSerializers, \
    ProjectBaselineDetailSerializers, ProjectBaselineUpdateSerializers


def get_project_obj(pk_idx):
    if TypeCheck.check_uuid(pk_idx):
        return Project.objects.filter_current(pk=pk_idx, fill__tenant=True, fill__company=True).first()
    return None


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
        operation_summary='Project baseline detail',
        operation_description='Get project baseline detail',
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="view",
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class ProjectBaselineUpdate(BaseUpdateMixin):
    queryset = ProjectBaseline.objects
    serializer_detail = ProjectBaselineUpdateSerializers
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

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
        operation_summary="Update project baseline",
        operation_description="Update Project baseline",
        request_body=ProjectBaselineUpdateSerializers,
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code="edit",
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)
