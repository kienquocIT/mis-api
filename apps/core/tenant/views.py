from copy import deepcopy

from rest_framework import generics, exceptions
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from apps.core.company.models import Company
from apps.core.hr.models import Group, Employee
from apps.core.base.models import Application, PlanApplication
from apps.core.base.serializers import ApplicationListSerializer
from apps.core.tenant.models import TenantPlan, Tenant
from apps.core.tenant.serializers import TenantPlanSerializer
from apps.shared import ResponseController, mask_view, TypeCheck

__all__ = [
    'TenantPlanList',
    'TenantApps',
    'TenantDiagram',
]


class TenantPlanList(generics.GenericAPIView):
    queryset = TenantPlan.objects
    search_fields = []

    serializer_class = TenantPlanSerializer

    @swagger_auto_schema(
        operation_summary="Tenant Plan list",
        operation_description="Get tenant plan list",
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(tenant_id=request.user.tenant_current_id)
        )
        serializer = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(serializer.data, key_data='result')


class TenantApps(APIView):
    queryset = Application.objects

    @swagger_auto_schema(
        operation_summary="Tenant Plan list",
        operation_description="Get tenant plan list",
    )
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        result = []
        plan_ids = TenantPlan.objects.filter(tenant_id=request.user.tenant_current_id).values_list('plan_id', flat=True)
        if plan_ids:
            objs = PlanApplication.objects.select_related('application').filter(plan_id__in=plan_ids)
            ser = ApplicationListSerializer([x.application for x in objs], many=True)
            result = ser.data
        return ResponseController.success_200(result, key_data='result')


class TenantDiagram(APIView):
    relationship_default = '000'  # no parent, no sibling, no children

    """
        type:
            0 = 'Tenant'
            1 = 'Company'
            2 = 'Department'
            3 = 'Employee'
        action:
            0 = 'parent'
            1 = 'children'
            2 = 'sibling'
            3 = 'families'
    """

    @classmethod
    def _get_relationship_employee(cls, employee_obj, has_sibling=None):
        data = str(deepcopy(cls.relationship_default))
        data = '1' + data[1:]  # auto parent is group
        if has_sibling is True or Employee.objects.filter_current(
                fill__tenant=True, fill__company=True, group_id=employee_obj.group_id
        ).exclude(id=employee_obj.id).exists():
            data = data[0:1] + '1' + data[2:]
        return data

    @classmethod
    def _get_relationship_group(cls, group_obj, has_sibling=None, has_children=None):
        data = str(deepcopy(cls.relationship_default))
        data = '1' + data[1:]  # auto parent is company
        if has_sibling is True or Group.objects.filter_current(
                fill__tenant=True, fill__company=True, parent_n=group_obj.parent_n
        ).exclude(id=group_obj.id).exists():
            data = data[0:1] + '1' + data[2:]
        if has_children is True or Employee.objects.filter_current(
                fill__tenant=True, fill__company=True,
                group_id=group_obj.id,
        ).exists():
            data = data[0:2] + '1'
        return data

    @classmethod
    def _get_relationship_company(cls, company_obj, has_sibling=None, has_children=None):
        data = str(deepcopy(cls.relationship_default))
        data = '1' + data[1:]  # auto parent is tenant
        if has_sibling is True or Company.objects.filter_current(
                tenant_id=company_obj.tenant_id, fill__tenant=True
        ).exists():
            data = data[0:1] + '1' + data[2:]
        if has_children is True or Group.objects.filter_current(
                company_id=company_obj.id,
                fill__tenant=True, fill__company=True
        ).exists():
            data = data[0:2] + '1'
        return data

    @classmethod
    def _get_relationship_tenant(cls, tenant_obj, has_children=None):
        data = str(deepcopy(cls.relationship_default))
        if has_children is True or Company.objects.filter_current(tenant_id=tenant_obj.id, fill__tenant=True).exists():
            data = data[0:2] + '1'
        return data

    @classmethod
    def _return_sibling(cls, data):
        return {'siblings': data if isinstance(data, list) else []}

    @classmethod
    def _return_children(cls, data):
        return {'children': data if isinstance(data, list) else []}

    def get_employee(self, pk_id, action):  # employee: type = 3
        try:
            employee_obj = Employee.objects.select_related('group').get_current(
                pk=pk_id,
                fill__tenant=True, fill__company=True
            )
        except Employee.DoesNotExist:
            raise exceptions.NotFound()

        if employee_obj and hasattr(employee_obj, 'id') and getattr(employee_obj, 'group_id', None):
            # make sure employee is objects and has group_id
            if action == '0':  # parent
                return {
                    'id': employee_obj.group_id,
                    'title': '**',
                    'name': employee_obj.group.title,
                    'relationship': self._get_relationship_group(group_obj=employee_obj.group),
                    'typeData': 2,
                }
            if action == '2':  # sibling
                arr = []
                employee_objs = Employee.objects.filter_current(
                    fill__tenant=True, fill__company=True, group_id=employee_obj.group_id
                ).exclude(id=employee_obj.id)
                has_sibling = employee_objs.count() >= 1
                for obj in employee_objs:
                    arr.append(
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.get_full_name(),
                            'avatar': obj.avatar if obj.avatar else None,
                            'relationship': self._get_relationship_employee(
                                employee_obj=employee_obj, has_sibling=has_sibling
                            ),
                            'typeData': 3,
                        }
                    )
                return self._return_sibling(data=arr)
            if action == '3':  # families
                group_obj = employee_obj.group
                manager_title = '**'
                if group_obj and group_obj.first_manager and group_obj.first_manager_id:
                    manager_title = group_obj.first_manager.get_full_name()
                children_objs = Employee.objects.filter_current(
                    fill__tenant=True, fill__company=True, group_id=group_obj.id
                ).exclude(id=employee_obj.id)
                children_has_sibling = children_objs.count() > 0
                return {
                    'id': employee_obj.group.id,
                    'name': employee_obj.group.title,
                    'title': manager_title,
                    'relationship': self._get_relationship_group(group_obj=group_obj, has_children=True),
                    'typeData': 2,
                    'children': [
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.get_full_name(),
                            'avatar': obj.avatar if obj.avatar else None,
                            'relationship': self._get_relationship_employee(
                                employee_obj=employee_obj, has_sibling=children_has_sibling
                            ),
                            'typeData': 3,
                        } for obj in children_objs
                    ]
                }
        raise exceptions.NotFound()

    def get_group(self, pk_id, action):  # group: type = 2
        try:
            group_obj = Group.objects.select_related('company').get_current(
                pk=pk_id,
                fill__tenant=True, fill__company=True
            )
        except Group.DoesNotExist:
            raise exceptions.NotFound()

        if group_obj and hasattr(group_obj, 'id') and getattr(group_obj, 'company_id', None):
            filter_get_child = {'parent_n__isnull': True}
            if group_obj.parent_n:
                filter_get_child = {'parent_n': group_obj.parent_n}

            if action == '0':  # parent
                if group_obj.parent_n:
                    return {
                        'id': group_obj.parent_n.id,
                        'title': '**',
                        'name': group_obj.parent_n.title,
                        'relationship': self._get_relationship_group(
                            group_obj=group_obj.parent_n, has_children=True
                        ),
                        'typeData': 2,
                    }
                return {
                    'id': group_obj.company_id,
                    'title': '**',
                    'name': group_obj.company.title,
                    'relationship': self._get_relationship_company(
                        company_obj=group_obj.company, has_children=True
                    ),
                    'typeData': 1,
                }
            if action == '1':  # children
                employee_objs = Employee.objects.filter_current(
                    group_id=group_obj.id,
                    fill__tenant=True,
                    fill__company=True
                )
                has_sibling = employee_objs.count() > 1
                arr = []
                for obj in employee_objs:
                    arr.append(
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.get_full_name(),
                            'avatar': obj.avatar if obj.avatar else None,
                            'relationship': self._get_relationship_employee(employee_obj=obj, has_sibling=has_sibling),
                            'typeData': 3,
                        }
                    )
                return self._return_children(data=arr)
            if action == '2':  # sibling
                group_objs = Group.objects.filter_current(
                    **filter_get_child,
                    fill__tenant=True, fill__company=True
                ).exclude(id=group_obj.id)
                has_sibling = group_objs.count() >= 1
                arr = []
                for obj in group_objs:
                    arr.append(
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.title,
                            'relationship': self._get_relationship_group(group_obj=obj, has_sibling=has_sibling),
                            'typeData': 2,
                        }
                    )
                return self._return_sibling(data=arr)
            if action == '3':  # families
                if group_obj.parent_n:
                    parent_data = {
                        'id': group_obj.parent_n.id,
                        'title': '**',
                        'name': group_obj.parent_n.title,
                        'relationship': self._get_relationship_group(
                            group_obj=group_obj.parent_n, has_children=True
                        ),
                        'typeData': 2,
                    }
                else:
                    parent_data = {
                        'id': group_obj.company_id,
                        'title': '**',
                        'name': group_obj.company.title,
                        'relationship': self._get_relationship_company(
                            company_obj=group_obj.company, has_children=True
                        ),
                        'typeData': 1,
                    }

                children_objs = Group.objects.filter_current(
                    **filter_get_child,
                    fill__tenant=True, fill__company=True,
                )
                has_sibling = children_objs.count() > 0
                return {
                    **parent_data,
                    'children': [
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.get_full_name(),
                            'relationship': self._get_relationship_group(
                                group_obj=obj, has_sibling=has_sibling,
                            ),
                            'typeData': 2,
                        } for obj in children_objs
                    ]
                }

        raise exceptions.NotFound()

    def get_company(self, pk_id, action):
        try:
            company_obj = Company.objects.get_current(pk=pk_id, fill__tenant=True)
        except Company.DoesNotExist:
            raise exceptions.NotFound()

        if company_obj and hasattr(company_obj, 'id'):
            if action == '0':  # parent
                return {
                    'id': company_obj.tenant.id,
                    'title': '**',
                    'name': company_obj.tenant.title,
                    'relationship': self._get_relationship_tenant(
                        tenant_obj=company_obj.tenant, has_children=True
                    ),
                    'typeData': 0,
                }
            if action == '1':  # children
                group_objs = Group.objects.filter_current(parent_n__isnull=True, fill__tenant=True, fill__company=True)
                has_sibling = group_objs.count() > 1
                arr = []
                for obj in group_objs:
                    arr.append(
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.title,
                            'relationship': self._get_relationship_group(group_obj=obj, has_sibling=has_sibling),
                            'typeData': 2,
                        }
                    )
                return self._return_children(data=arr)
            if action == '2':  # siblings
                company_objs = Company.objects.filter_current(tenant=company_obj.tenant, fill__tenant=True).exclude(
                    id=company_obj.id
                )
                has_siblings = company_objs.count() > 0
                arr = []
                for obj in company_objs:
                    arr.append(
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.title,
                            'relationship': self._get_relationship_company(company_obj=obj, has_sibling=has_siblings),
                            'typeData': 1,
                        }
                    )
                return self._return_sibling(data=arr)
            if action == '3':  # families
                parent_data = {
                    'id': company_obj.tenant.id,
                    'title': '**',
                    'name': company_obj.tenant.title,
                    'relationship': self._get_relationship_tenant(
                        tenant_obj=company_obj.tenant, has_children=True
                    ),
                    'typeData': 0,
                }
                children_objs = Company.objects.filter_current(
                    tenant=company_obj.tenant,
                    fill__tenant=True
                ).exclude(id=company_obj.id)
                has_sibling = children_objs.count() > 0
                return {
                    **parent_data,
                    'children': [
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.title,
                            'relationship': self._get_relationship_company(
                                company_obj=obj, has_sibling=has_sibling,
                            ),
                            'typeData': 1,
                        } for obj in children_objs
                    ]
                }
        raise exceptions.NotFound()

    def get_tenant(self, pk_id, action):
        try:
            if pk_id == self.request.user.tenant_current_id:
                tenant_obj = Tenant.objects.get_current(id=pk_id)
            else:
                raise exceptions.NotFound()
        except Tenant.DoesNotExist:
            raise exceptions.NotFound()

        if tenant_obj and hasattr(tenant_obj, 'id'):
            if action == '1':  # children
                company_objs = Company.objects.filter_current(tenant=tenant_obj, fill__tenant=True)
                has_sibling = company_objs.count() > 1
                arr = []
                for obj in company_objs:
                    arr.append(
                        {
                            'id': obj.id,
                            'title': '**',
                            'name': obj.title,
                            'relationship': self._get_relationship_company(company_obj=obj, has_sibling=has_sibling),
                            'typeData': 1,
                        }
                    )
                return self._return_children(data=arr)
        raise exceptions.NotFound()

    def _first_current_sequent_department(self, employee_obj):
        main_group = employee_obj.group
        if main_group and hasattr(main_group, 'id'):
            tree_data = {
                'id': main_group.id,
                'name': main_group.title,
                'title': '**',
                'relationship': self._get_relationship_group(
                    group_obj=main_group, has_children=True,
                ),
                'typeData': 2,
                'children': [{
                    'id': employee_obj.id,
                    'name': employee_obj.get_full_name(),
                    'title': '**',
                    'avatar': employee_obj.avatar if employee_obj.avatar else None,
                    'relationship': self._get_relationship_employee(
                        employee_obj=employee_obj,
                    ),
                    'typeData': 3,
                }],
            }
            counter = 20
            group_start = main_group.parent_n
            while group_start is not None or counter > 20:
                tree_data = {
                    'id': group_start.id,
                    'name': group_start.title,
                    'title': '**',
                    'relationship': self._get_relationship_group(
                        group_obj=group_start, has_children=True,
                    ),
                    'typeData': 2,
                    'children': [tree_data],
                }
                group_start = group_start.parent_n
            return tree_data
        return {}

    def get_first_current(self):
        employee_obj = self.request.user.employee_current
        if employee_obj and hasattr(employee_obj, 'id'):
            data_tmp = self._first_current_sequent_department(employee_obj=employee_obj)
            if data_tmp:
                employee_group_data = [self._first_current_sequent_department(employee_obj=employee_obj)]
            else:
                employee_group_data = []
        else:
            employee_group_data = []

        return {
            'id': self.request.user.tenant_current.id,
            'name': self.request.user.tenant_current.title,
            'title': '**',
            'relationship': self._get_relationship_tenant(tenant_obj=self.request.user.tenant_current),
            'typeData': 0,
            'children': [
                {
                    'id': self.request.user.company_current.id,
                    'name': self.request.user.company_current.title,
                    'title': '**',
                    'relationship': self._get_relationship_company(company_obj=self.request.user.company_current),
                    'typeData': 1,
                    'children': employee_group_data,
                },
            ]
        }

    def parse_params(self, params_dict: dict):
        if self.request.user.tenant_current_id:
            _get_first_current = params_dict.get('first_current', False) in [1, '1']
            if _get_first_current is True:
                return self.get_first_current()
            _type = params_dict.get('type', None)
            _action = params_dict.get('action', None)
            _id = params_dict.get('id', None)
            if (
                    _id and
                    TypeCheck.check_uuid(_id) and
                    _type in ['0', '1', '2', '3'] and
                    _action in ['0', '1', '2']
            ):
                if _type == '0':
                    return self.get_tenant(pk_id=_id, action=_action)
                if _type == '1':
                    return self.get_company(pk_id=_id, action=_action)
                if _type == '2':
                    return self.get_group(pk_id=_id, action=_action)
                if _type == '3':
                    return self.get_employee(pk_id=_id, action=_action)
            return {}
        raise exceptions.NotFound()

    @swagger_auto_schema(operation_summary='Org Chart Company')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        result = self.parse_params(params_dict=request.query_params.dict())
        return ResponseController.success_200(data=result, key_data='result')
