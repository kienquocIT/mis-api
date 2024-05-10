__all__ = ['ProjectTaskList']

from typing import Union
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from ..models import ProjectMapTasks, ProjectMapMember, Project
from apps.shared import BaseListMixin, mask_view, TypeCheck, ResponseController, BaseCreateMixin
from ..serializers import ProjectTaskListSerializers, ProjectTaskCreateSerializers, ProjectTaskDetailSerializers


class ProjectTaskList(BaseListMixin, BaseCreateMixin):
    queryset = ProjectMapTasks.objects
    serializer_list = ProjectTaskListSerializers
    serializer_create = ProjectTaskCreateSerializers
    serializer_detail = ProjectTaskDetailSerializers
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related("task")

    @property
    def filter_kwargs(self) -> dict[str, any]:
        return {
            **self.cls_check.attr.setup_hidden(from_view='list'),
        }

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        return self.list_empty()

    @classmethod
    def get_pj_obj(cls, pk_idx):
        if TypeCheck.check_uuid(pk_idx):
            return Project.objects.filter_current(pk=pk_idx, fill__tenant=True, fill__company=True).first()
        return None

    def get_pj_member_of_current_user(self, pj_obj):
        return ProjectMapMember.objects.filter_current(
            project=pj_obj,
            member=self.cls_check.employee_attr.employee_current,
            fill__tenant=True, fill__company=True
        ).first()

    def check_permit_add_member_pj(self, pj_obj) -> bool:
        # special case skip with True if current user is employee_inherit
        emp_id = self.cls_check.employee_attr.employee_current_id
        if emp_id and str(pj_obj.employee_inherit_id) == str(emp_id):
            self.ser_context["has_permit_add"] = True
            return True

        pj_member_current_user = self.get_pj_member_of_current_user(pj_obj=pj_obj)
        if pj_member_current_user:
            self.ser_context["has_permit_add"] = pj_member_current_user.permit_add_gaw,
            return pj_member_current_user.permit_add_gaw
        return False

    def get_lookup_url_kwarg(self) -> dict:
        return {
            'project_id': self.kwargs['pk_pj'],
        }

    @swagger_auto_schema(
        operation_summary="Project task list",
        operation_description="get project task list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        label_code='project', model_code='project', perm_code='view',
    )
    def get(self, request, *args, pk_pj, **kwargs):
        pj_obj = self.get_pj_obj(pk_pj)
        if pj_obj:
            if self.check_permit_add_member_pj(pj_obj=pj_obj):
                return self.list(request, *args, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()

    @swagger_auto_schema(
        operation_summary="Project task create",
        operation_description="create project map with task",)
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, pk_pj, **kwargs):
        self.ser_context = {
            "employee_current": request.user.employee_current_id
        }
        pj_obj = self.get_pj_obj(pk_pj)
        if pj_obj:
            if self.check_permit_add_member_pj(pj_obj=pj_obj):
                setattr(self, 'project_id', pj_obj.id)
                return self.create(request, *args, pj_obj, **kwargs)
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()
