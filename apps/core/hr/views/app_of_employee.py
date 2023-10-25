from typing import Union

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.response import Response

from apps.core.hr.filters import EmployeeStorageAppAllListFilter
from apps.core.hr.models import Employee, DistributionApplication
from apps.core.hr.serializers.app_of_employee import AllApplicationOfEmployeeSerializer
from apps.shared import BaseListMixin, mask_view, TypeCheck

from apps.sales.opportunity.models import OpportunitySaleTeamMember


class EmployeeStorageAppAllList(BaseListMixin):
    queryset = DistributionApplication.objects
    search_fields = ["app__title"]
    serializer_list = AllApplicationOfEmployeeSerializer
    filterset_class = EmployeeStorageAppAllListFilter

    def get_queryset(self):
        return super().get_queryset().select_related('app')

    @property
    def filter_kwargs(self) -> dict[str, any]:
        return {
            'employee_id': self.kwargs['pk'],
            'company_id': self.cls_check.employee_attr.company_id,
            'tenant_id': self.cls_check.employee_attr.tenant_id,
        }

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:  # pylint: disable=R0912
        try:
            employee_obj = Employee.objects.get(pk=self.kwargs['pk'])
        except Employee.DoesNotExist:
            raise exceptions.NotFound

        if self.__opportunity_id:
            #
            # check permit for Opp in here!
            #
            if self.cls_check.employee_attr.employee_current_id:
                member_ids = list({str(self.cls_check.employee_attr.employee_current_id), str(employee_obj.id)})
                opp_member_objs = OpportunitySaleTeamMember.objects.filter_current(
                    fill__tenant=True, fill__company=True,
                    opportunity_id=self.__opportunity_id, member_id__in=member_ids
                )
                if len(member_ids) == 1 and opp_member_objs.count() == 1:
                    opp_member = opp_member_objs.first()
                    state = (
                            opp_member.permit_view_this_opp is True
                            or opp_member.permit_add_member is True
                            or (
                                    self.cls_check.employee_attr.employee_current_id ==
                                    opp_member.opportunity.employee_inherit_id
                            )
                    )
                elif len(member_ids) == 2 and opp_member_objs.count() == 2:
                    opp_member = None
                    for obj in opp_member_objs:
                        if str(obj.member_id) == str(self.cls_check.employee_attr.employee_current_id):
                            opp_member = obj

                    if opp_member:
                        state = (
                                opp_member.permit_view_this_opp is True
                                or opp_member.permit_add_member is True
                                or (
                                        self.cls_check.employee_attr.employee_current_id ==
                                        opp_member.opportunity.employee_inherit_id
                                )
                        )
                    else:
                        state = False
                else:
                    state = False
            else:
                # current user not related employee -> deny permit!
                state = False
        elif self.__project_id:
            #
            # update check permit for Project in here!
            #
            if self.cls_check.employee_attr.employee_current_id:
                ...
            state = False
        else:
            #
            # auto check permit general in Employee Obj (hr.employee.view)
            #
            state = self.check_perm_by_obj_or_body_data(obj=employee_obj, auto_check=True)

        if state is True:
            if self.__opportunity_id:
                # exclude app opportunity
                return ~Q(app_id='296a1410-8d72-46a8-a0a1-1821f196e66c')
            if self.__project_id:
                # exclude app project
                ...
            return Q()
        return self.list_empty()

    __opportunity_id = None
    __project_id = None

    @swagger_auto_schema(
        operation_summary="Application List of Employee",
        operation_description="Application List of Employee",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            self.__opportunity_id = request.query_params.dict().get('opportunity', None)
            self.__project_id = request.query_params.dict().get('project', None)
            return self.list(request, *args, pk, **kwargs)
        return self.list_empty()
