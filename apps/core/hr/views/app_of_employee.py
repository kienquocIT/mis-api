from typing import Union

from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.response import Response

from apps.core.hr.filters import EmployeeStorageAppAllListFilter
from apps.core.hr.models import (
    Employee, PlanEmployee, PlanEmployeeApp,
    RoleHolder,
    PlanRole, PlanRoleApp,
    DistributionPlan, DistributionApplication, EmployeePermission, RolePermission,
)
from apps.core.hr.serializers.app_of_employee import (
    AllApplicationOfEmployeeSerializer,
    SummaryApplicationOfEmployeeSerializer,
)
from apps.sales.project.models import ProjectMapMember
from apps.shared import BaseListMixin, mask_view, TypeCheck, ResponseController, BaseMixin

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
            state = False
            if self.cls_check.employee_attr.employee_current_id:
                member_ids = list({str(self.cls_check.employee_attr.employee_current_id), str(employee_obj.id)})
                pj_member_objs = ProjectMapMember.objects.filter_current(
                    fill__tenant=True, fill__company=True,
                    project_id=self.__project_id, member_id__in=member_ids
                )
                if len(member_ids) == 1 and pj_member_objs.count() == 1:
                    pj_member = pj_member_objs.first()
                    state = (
                            pj_member.permit_view_this_project is True
                            or pj_member.permit_add_member is True
                            or (
                                    self.cls_check.employee_attr.employee_current_id ==
                                    pj_member.project.employee_inherit_id
                            )
                    )
                elif len(member_ids) == 2 and pj_member_objs.count() == 2:
                    pj_member = None
                    for obj in pj_member_objs:
                        if str(obj.member_id) == str(self.cls_check.employee_attr.employee_current_id):
                            pj_member = obj
                            break
                    if pj_member:
                        state = (
                                pj_member.permit_view_this_project is True
                                or pj_member.permit_add_member is True
                                or (
                                        self.cls_check.employee_attr.employee_current_id ==
                                        pj_member.project.employee_inherit_id
                                )
                        )
        else:
            #
            # auto check permit general in Employee Obj (hr.employee.view)
            #
            state = self.check_perm_by_obj_or_body_data(obj=employee_obj, auto_check=True)

        if state is True:
            if self.__opportunity_id or self.__project_id:
                # exclude app opportunity and project
                return ~Q(app_id__in=['49fe2eb9-39cd-44af-b74a-f690d7b61b67', '296a1410-8d72-46a8-a0a1-1821f196e66c'])
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


class EmployeeStorageAppSummaryList(BaseMixin):
    queryset = DistributionApplication.objects
    serializer_list = SummaryApplicationOfEmployeeSerializer

    @staticmethod
    def parse_app_data(obj, key='application'):
        application = getattr(obj, key)
        return {
            "id": application.id,
            "title": application.title,
            "code": application.code,
        }

    @classmethod
    def get_app_by_role(cls, employee_obj):
        result = []
        for role_holder_obj in RoleHolder.objects.filter(employee=employee_obj):
            result.append(
                {
                    'id': role_holder_obj.role.id,
                    'title': role_holder_obj.role.title,
                    'code': role_holder_obj.role.code,
                    'application': [
                        cls.parse_app_data(obj) for obj in
                        PlanRoleApp.objects.select_related('application').filter(
                            plan_role__role=role_holder_obj.role
                        ).order_by(
                            'application__title'
                        )
                        if obj.application
                    ]
                }
            )
        return result

    @classmethod
    def get_app_by_employee(cls, employee_obj):
        return [
            cls.parse_app_data(obj) for obj in
            PlanEmployeeApp.objects.select_related('application').filter(plan_employee__employee=employee_obj).order_by(
                'application__title'
            ) if obj.application
        ]

    @classmethod
    def get_app_by_summary(cls, employee_obj):
        return [
            cls.parse_app_data(obj, key='app')
            for obj in
            DistributionApplication.objects.select_related('app').filter(employee=employee_obj).order_by('app__title')
            if obj.app
        ]

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
            try:
                employee_obj = Employee.objects.get_current(fill__tenant=True, fill__company=True, pk=pk)
            except Employee.DoesNotExist:
                raise exceptions.NotFound

            if self.check_perm_by_obj_or_body_data(obj=employee_obj, auto_check=True):
                return ResponseController.success_200(
                    data={
                        'employee': self.get_app_by_employee(employee_obj=employee_obj),
                        'roles': self.get_app_by_role(employee_obj=employee_obj),
                        'summary': self.get_app_by_summary(employee_obj=employee_obj),
                    }, key_data='result'
                )

            raise exceptions.PermissionDenied
        return ResponseController.success_200(data=[], key_data='result')


class EmployeeStoragePlanSummaryList(BaseListMixin):
    queryset = DistributionApplication.objects
    serializer_list = SummaryApplicationOfEmployeeSerializer

    @staticmethod
    def parse_plan_data(obj, key='plan'):
        plan = getattr(obj, key)
        return {
            'id': plan.id,
            'title': plan.title,
            'code': plan.code,
        }

    @classmethod
    def get_plan_by_employee(cls, employee_obj):
        return [
            cls.parse_plan_data(obj)
            for obj in
            PlanEmployee.objects.select_related('plan').filter(employee=employee_obj).order_by('plan__title')
            if obj.plan
        ]

    @classmethod
    def get_plan_by_role(cls, employee_obj):
        result = []
        for role_holder_obj in RoleHolder.objects.filter(employee=employee_obj):
            result.append(
                {
                    'id': role_holder_obj.role.id,
                    'title': role_holder_obj.role.title,
                    'code': role_holder_obj.role.code,
                    'plan': [
                        cls.parse_plan_data(obj) for obj in
                        PlanRole.objects.select_related('plan').filter(
                            role=role_holder_obj.role
                        ).order_by(
                            'plan__title'
                        )
                        if obj.plan
                    ]
                }
            )
        return result

    @classmethod
    def get_plan_by_summary(cls, employee_obj):
        return [
            {
                'tenant_plan': {
                    'id': obj.tenant_plan.id,
                    'purchase_order': obj.tenant_plan.purchase_order,
                    'date_active': obj.tenant_plan.date_active,
                    'date_end': obj.tenant_plan.date_end,
                    'license_quantity': obj.tenant_plan.license_quantity,
                    'license_used': obj.tenant_plan.license_used,
                    'is_limited': obj.tenant_plan.is_limited,
                    'is_expired': obj.tenant_plan.is_expired,
                },
                'plan': cls.parse_plan_data(obj),
            }
            for obj in
            DistributionPlan.objects.select_related('plan', 'tenant_plan').filter(employee=employee_obj).order_by(
                'plan__title'
            )
            if obj.plan
        ]

    @swagger_auto_schema(
        operation_summary="Plan List of Employee",
        operation_description="Plan List of Employee",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            try:
                employee_obj = Employee.objects.get_current(fill__tenant=True, fill__company=True, pk=pk)
            except Employee.DoesNotExist:
                raise exceptions.NotFound

            if self.check_perm_by_obj_or_body_data(obj=employee_obj, auto_check=True):
                return ResponseController.success_200(
                    data={
                        'employee': self.get_plan_by_employee(employee_obj=employee_obj),
                        'roles': self.get_plan_by_role(employee_obj=employee_obj),
                        'summary': self.get_plan_by_summary(employee_obj=employee_obj),
                    }, key_data='result'
                )

            raise exceptions.PermissionDenied
        return self.list_empty()


class EmployeeStoragePermissionSummaryList(BaseListMixin):
    queryset = DistributionApplication.objects
    serializer_list = SummaryApplicationOfEmployeeSerializer

    @classmethod
    def get_permit_of_employee(cls, employee_obj):
        try:
            permit_obj = EmployeePermission.objects.get(employee=employee_obj)
            return permit_obj.permission_by_configured
        except EmployeePermission.DoesNotExist:
            pass
        return []

    @classmethod
    def get_permit_role_of_employee(cls, employee_obj):
        result = []
        for role_holder_obj in RoleHolder.objects.filter(employee=employee_obj):
            try:
                role_permit_obj = RolePermission.objects.get(role=role_holder_obj.role)
            except RolePermission.DoesNotExist:
                continue

            result.append(
                {
                    'id': role_holder_obj.role.id,
                    'title': role_holder_obj.role.title,
                    'code': role_holder_obj.role.code,
                    'permission_by_configured': role_permit_obj.permission_by_configured
                }
            )
        return result

    @swagger_auto_schema(
        operation_summary="Plan List of Employee",
        operation_description="Plan List of Employee",
    )
    @mask_view(
        login_require=True, auth_require=False,
        allow_admin_tenant=True, allow_admin_company=True,
        label_code='hr', model_code='employee', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            try:
                employee_obj = Employee.objects.get_current(fill__tenant=True, fill__company=True, pk=pk)
            except Employee.DoesNotExist:
                raise exceptions.NotFound

            if self.check_perm_by_obj_or_body_data(obj=employee_obj, auto_check=True):
                return ResponseController.success_200(
                    data={
                        'employee': self.get_permit_of_employee(employee_obj=employee_obj),
                        'roles': self.get_permit_role_of_employee(employee_obj=employee_obj),
                    }, key_data='result',
                )
            raise exceptions.PermissionDenied
        return self.list_empty()
