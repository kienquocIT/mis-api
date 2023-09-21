from copy import deepcopy

from rest_framework import generics, exceptions
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Max

from apps.core.company.models import Company
from apps.core.hr.models import Group, Employee, GroupLevel
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
    default_group_filter = {'company_id': ''}

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
                group_id=employee_obj.group_id, is_active=True, is_delete=False,
                fill__tenant=True, fill__company=True,
        ).exclude(id=employee_obj.id).exists():
            data = data[0:1] + '1' + data[2:]
        return data

    @classmethod
    def _get_relationship_group(cls, group_obj, has_sibling=None, has_children=None):
        data = str(deepcopy(cls.relationship_default))
        data = '1' + data[1:]  # auto parent is company
        if has_sibling is True or Group.objects.filter_current(
                parent_n=group_obj.parent_n, is_delete=False,
                fill__tenant=True, fill__company=True,
        ).exclude(id=group_obj.id).exists():
            data = data[0:1] + '1' + data[2:]
        if has_children is True or Employee.objects.filter_current(
                group_id=group_obj.id, is_active=True, is_delete=False,
                fill__tenant=True, fill__company=True,
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
                company_id=company_obj.id, is_delete=False,
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

    @classmethod
    def _parse_employee__title(cls, employee_obj):
        role_title_arr = [x.title for x in employee_obj.role.all()]
        if len(role_title_arr) > 0:
            return ", ".join(role_title_arr)
        return '**'

    @classmethod
    def get_max_level(cls):
        level_num = GroupLevel.objects.filter_current(
            fill__tenant=True, fill__company=True
        ).aggregate(Max('level'))['level__max']
        if isinstance(level_num, int):
            return level_num
        return 0

    @classmethod
    def get_level_offset__group(cls, group_obj, from_group, is_call_children=False):
        if from_group and hasattr(from_group, 'id'):
            offset_minus = group_obj.group_level.level - from_group.group_level.level
            if offset_minus > 0:
                if is_call_children is True:
                    return offset_minus - 1
                return offset_minus
        return 0

    @classmethod
    def get_level_offset__employee(cls, from_group, max_level):
        if from_group and hasattr(from_group, 'id'):
            offset_minus = max_level - from_group.group_level.level
            if offset_minus > 0:
                return offset_minus
        elif max_level:
            return max_level
        return 0

    def _parse__tenant(self, tenant_obj, **kwargs):
        return {
            'id': tenant_obj.id,
            'name': tenant_obj.title,
            'title': tenant_obj.representative_fullname,
            'relationship': self._get_relationship_tenant(tenant_obj=tenant_obj),
            'typeData': 0,
            'levelOffset': 0,
        }

    def _parse__company(self, company_obj, **kwargs):
        has_children = kwargs.get('has_children', None)
        has_sibling = kwargs.get('has_sibling', None)

        data = {
            'id': company_obj.id,
            'title': company_obj.representative_fullname,
            'name': company_obj.title,
            'relationship': self._get_relationship_company(
                company_obj=company_obj, has_sibling=has_sibling, has_children=has_children
            ),
            'typeData': 1,
            'levelOffset': 0,
        }

        set_current_deny_other = kwargs.get('set_current_deny_other', False)
        if set_current_deny_other is True:
            data['is_current'] = company_obj.id == self.request.user.company_current_id
            data['relationship'] = data['relationship'] \
                if company_obj.id == self.request.user.company_current_id else '100'

        return data

    def _parse__group(self, group_obj, **kwargs):
        has_children = kwargs.get('has_children', None)
        has_sibling = kwargs.get('has_sibling', None)
        from_group = kwargs.get('from_group', None)
        is_call_children = kwargs.get('is_call_children', False)

        manager_title = '**'
        if group_obj and group_obj.first_manager and group_obj.first_manager_id:
            manager_title = group_obj.first_manager.get_full_name()
        group_level = group_obj.group_level.level if group_obj.group_level else 1

        return {
            'id': group_obj.id,
            'title': manager_title,
            'name': group_obj.title,
            'relationship': self._get_relationship_group(
                group_obj=group_obj, has_children=has_children, has_sibling=has_sibling
            ),
            'group_level': group_level,
            'typeData': 2,
            'levelOffset': self.get_level_offset__group(
                group_obj=group_obj, from_group=from_group, is_call_children=is_call_children
            ),
        }

    def _parse__employee(self, employee_obj, **kwargs):
        has_sibling = kwargs.get('has_sibling', None)
        from_group = kwargs.get('from_group', None)
        max_level = kwargs.get('max_level', None)

        return {
            'id': employee_obj.id,
            'title': self._parse_employee__title(employee_obj),
            'name': employee_obj.get_full_name(),
            'avatar': employee_obj.avatar if employee_obj.avatar else None,
            'relationship': self._get_relationship_employee(
                employee_obj=employee_obj, has_sibling=has_sibling
            ),
            'typeData': 3,
            'levelOffset': self.get_level_offset__employee(
                from_group=from_group, max_level=max_level,
            ),
        }

    ######################################
    # GET ON DEMAND
    # Action:
    #   - Parent
    #   - Sibling
    #   - Children
    #   - Families
    ######################################

    def get_on_demand__tenant(self, pk_id, action):
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
                return self._return_children(
                    data=[
                        self._parse__company(
                            company_obj=obj, has_sibling=has_sibling, set_current_deny_other=True
                        ) for obj in company_objs
                    ]
                )
        raise exceptions.NotFound()

    def get_on_demand__company(self, pk_id, action):
        try:
            if pk_id == str(self.request.user.company_current_id):
                company_obj = Company.objects.get_current(pk=pk_id, fill__tenant=True)
            else:
                raise exceptions.NotFound()
        except Company.DoesNotExist:
            raise exceptions.NotFound()

        if company_obj and hasattr(company_obj, 'id'):
            if action == '0':  # parent
                return self._parse__tenant(company_obj.tenant)
            if action == '1':  # children
                group_objs = Group.objects.select_related('group_level').filter_current(
                    parent_n__isnull=True, is_delete=False,
                    fill__tenant=True, fill__company=True
                )
                has_sibling = group_objs.count() > 1
                return self._return_children(
                    data=[
                        self._parse__group(group_obj=obj, has_sibling=has_sibling) for obj in group_objs
                    ]
                )
            if action == '2':  # siblings
                company_objs = Company.objects.filter_current(tenant=company_obj.tenant, fill__tenant=True).exclude(
                    id=company_obj.id
                )
                has_siblings = company_objs.count() > 0
                return self._return_sibling(
                    data=[
                        self._parse__company(
                            company_obj=obj, has_sibling=has_siblings, set_current_deny_other=True
                        ) for obj in company_objs
                    ]
                )
            if action == '3':  # families
                children_objs = Company.objects.filter_current(tenant=company_obj.tenant, fill__tenant=True).exclude(
                    id=company_obj.id
                )
                has_sibling = children_objs.count() > 0
                return {
                    **self._parse__tenant(tenant_obj=company_obj.tenant),
                    'children': [
                        self._parse__company(
                            company_obj=obj, has_sibling=has_sibling, set_current_deny_other=True
                        ) for obj in children_objs
                    ]
                }

        raise exceptions.NotFound()

    def get_on_demand__group(self, pk_id, action):
        try:
            group_obj = Group.objects.select_related('company').get_current(
                pk=pk_id, is_delete=False,
                fill__tenant=True, fill__company=True
            )
        except Group.DoesNotExist:
            raise exceptions.NotFound()

        if group_obj and hasattr(group_obj, 'id'):
            if action == '0':  # parent
                if group_obj.parent_n_id:
                    return self._parse__group(group_obj=group_obj.parent_n)
                return self._parse__company(company_obj=group_obj.company, has_children=True)
            if action == '1':  # children
                result = []

                # group children
                child_group_objs = Group.objects.filter_current(
                    parent_n_id=group_obj.id, is_delete=False,
                    fill__tenant=True, fill__company=True
                ).exclude(id=group_obj.id)
                child_group_sibling = child_group_objs.count() > 1
                result += [
                    self._parse__group(
                        group_obj=obj, has_sibling=child_group_sibling, from_group=group_obj, is_call_children=True,
                    ) for obj in child_group_objs
                ]

                # employee children
                max_level = self.get_max_level()
                child_employee_objs = Employee.objects.filter_current(
                    group_id=group_obj.id, is_active=True, is_delete=False,
                    fill__tenant=True, fill__company=True
                )
                child_employee_sibling = child_employee_objs.count() > 1
                result += [
                    self._parse__employee(
                        employee_obj=obj, has_sibling=child_employee_sibling, from_group=group_obj, max_level=max_level
                    ) for obj in child_employee_objs
                ]

                return self._return_children(data=result)
            if action == '2':  # sibling
                if group_obj.parent_n_id:
                    filter_group = {'parent_n_id': group_obj.parent_n_id}
                else:
                    filter_group = {'parent_n_id__isnull': True}

                children_objs = Group.objects.filter_current(
                    **filter_group, is_delete=False,
                    fill__tenant=True, fill__company=True,
                ).exclude(id=group_obj.id)
                has_sibling = children_objs.count() > 0

                return self._return_sibling(
                    data=[
                        self._parse__group(
                            group_obj=obj, has_sibling=has_sibling, from_group=group_obj,
                        ) for obj in children_objs
                    ]
                )

            if action == '3':  # families
                if group_obj.parent_n_id:
                    parent_data = self._parse__group(group_obj=group_obj.parent_n)
                else:
                    parent_data = self._parse__company(company_obj=group_obj.company, has_children=True)

                children_objs = Group.objects.filter_current(
                    is_delete=False,
                    fill__tenant=True, fill__company=True,
                ).exclude(id=group_obj.id)
                has_sibling = children_objs.count() > 0
                return {
                    **parent_data,
                    'children': [
                        self._parse__group(
                            group_obj=obj, has_sibling=has_sibling, from_group=group_obj
                        ) for obj in children_objs
                    ]
                }

        raise exceptions.NotFound()

    def get_on_demand__employee(self, pk_id, action):
        try:
            employee_obj = Employee.objects.select_related('group').get_current(
                pk=pk_id, is_active=True, is_delete=False,
                fill__tenant=True, fill__company=True
            )
        except Employee.DoesNotExist:
            raise exceptions.NotFound()

        if employee_obj and hasattr(employee_obj, 'id') and getattr(employee_obj, 'group_id', None):
            if action == '0':  # parent
                return self._parse__group(group_obj=employee_obj.group)
            if action == '1':  # children
                ...
            if action == '2':  # sibling
                child_objs = Employee.objects.filter_current(
                    group=employee_obj.group, is_active=True, is_delete=False,
                    fill__tenant=True, fill__company=True
                ).exclude(id=employee_obj.id)
                has_sibling = child_objs.count() > 1
                max_level = self.get_max_level()
                return self._return_sibling(
                    data=[
                        self._parse__employee(
                            employee_obj=obj, has_sibling=has_sibling,
                            from_group=employee_obj.group, max_level=max_level,
                        ) for obj in child_objs
                    ]
                )
            if action == '3':  # families
                child_objs = Employee.objects.filter_current(
                    group=employee_obj.group, is_active=True, is_delete=False,
                    fill__tenant=True, fill__company=True
                ).exclude(id=employee_obj.id)
                has_sibling = child_objs.count() > 1
                return {
                    **self._parse__group(group_obj=employee_obj.group),
                    'children': [
                        self._parse__employee(employee_obj=obj, has_sibling=has_sibling) for obj in child_objs
                    ]
                }

        raise exceptions.NotFound()

    ######################################
    # // GET ON DEMAND
    ######################################

    ######################################
    # GET FIRST
    ######################################

    def _first_current_sequent_department(self, employee_obj):
        main_group = employee_obj.group
        if main_group and hasattr(main_group, 'id'):
            max_level = self.get_max_level()
            tree_data = {
                **self._parse__group(group_obj=main_group),
                'children': [
                    self._parse__employee(
                        employee_obj=employee_obj,
                        from_group=main_group,
                        max_level=max_level
                    ),
                ],
            }
            counter = 20
            group_start = main_group.parent_n
            while group_start is not None or counter > 20:
                tree_data = {
                    **self._parse__group(group_obj=group_start),
                    'children': [tree_data],
                }
                group_start = group_start.parent_n
            return tree_data
        return {}

    def get_first_current(self):
        employee_id = self.request.user.employee_current_id
        if employee_id:
            try:
                employee_obj = Employee.objects.prefetch_related('role').get_current(
                    pk=employee_id, is_active=True, is_delete=False,
                    fill__tenant=True, fill__company=True
                )
                data_tmp = self._first_current_sequent_department(employee_obj=employee_obj)
                if data_tmp:
                    employee_group_data = [data_tmp]
                else:
                    employee_group_data = []
            except Employee.DoesNotExist:
                raise exceptions.NotFound()
        else:
            employee_group_data = []

        tenant_data = self._parse__tenant(tenant_obj=self.request.user.tenant_current)
        return {
            **tenant_data,
            'children': [
                {
                    **self._parse__company(company_obj=self.request.user.company_current, set_current_deny_other=True),
                    'children': employee_group_data
                }
            ]
        }

    ######################################
    #  // GET FIRST
    ######################################

    ######################################
    # GET ALL
    ######################################

    def get_all_children_of_group(self, group_id):
        result = []

        # group children
        child_group_objs = Group.objects.filter_current(
            parent_n_id=group_id, is_delete=False,
            fill__tenant=True, fill__company=True
        )
        child_group_sibling = child_group_objs.count() > 1
        result += [
            self._parse__group(
                group_obj=obj, has_sibling=child_group_sibling,
            ) for obj in child_group_objs
        ]

        # employee children
        child_employee_objs = Employee.objects.filter_current(
            group_id=group_id, is_active=True, is_delete=False,
            fill__tenant=True, fill__company=True,
        )
        child_employee_sibling = child_employee_objs.count() > 1
        result += [
            self._parse__employee(
                employee_obj=obj, has_sibling=child_employee_sibling,
            ) for obj in child_employee_objs
        ]

        return result

    def get_all_group_not_parent(self):
        group_objs = Group.objects.filter_current(
            parent_n__isnull=True, is_delete=False,
            fill__tenant=True, fill__company=True,
        )
        has_sibling = group_objs.count() > 1
        return [
            self._parse__group(
                group_obj=obj, has_sibling=has_sibling
            ) for obj in group_objs
        ]

    def get_all_by_current(self, all_option, group_id=None):
        user_obj = self.request.user
        if all_option is None or all_option == '0':
            if user_obj.tenant_current and user_obj.tenant_current_id:
                # get tenant + all company
                return {
                    'group_count': Group.objects.filter_current(
                        is_delete=False,
                        fill__tenant=True, fill__company=True
                    ).count(),
                    'max_level': self.get_max_level(),

                    **self._parse__tenant(tenant_obj=user_obj.tenant_current),
                    'children': [
                        {
                            **self._parse__company(company_obj=company_obj, set_current_deny_other=True),
                            'children': [],
                        } for company_obj in Company.objects.filter(tenant_id=user_obj.tenant_current_id)
                    ]
                }
            return {}
        if all_option == '1':
            # get all group of current company
            # return self.get_all_summary_group()
            return self.get_all_group_not_parent()
        if all_option == '2':
            # get employee of group
            if group_id and TypeCheck.check_uuid(group_id):
                return self.get_all_children_of_group(group_id=group_id)
            return []
        return {}

    ######################################
    # // GET ALL
    ######################################

    def parse_params(self, params_dict: dict):  # pylint: disable=R0911
        if self.request.user.tenant_current_id:
            # all structure of company current + label of tenant (not get another company)
            _get_all_of_company = params_dict.get('get_all', '0') in [1, '1']
            if _get_all_of_company is True:
                _get_all_option = params_dict.get('get_all_option', None)
                group_id = params_dict.get('get_all__group_id', None)
                return self.get_all_by_current(all_option=_get_all_option, group_id=group_id)

            # structure first level from tenant to employee request (to company when user not linked employee)
            _get_first_current = params_dict.get('first_current', '0') in [1, '1']
            if _get_first_current is True:
                return self.get_first_current()

            # utility get parent, children, sibling, families
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
                    return self.get_on_demand__tenant(pk_id=_id, action=_action)
                if _type == '1':
                    return self.get_on_demand__company(pk_id=_id, action=_action)
                if _type == '2':
                    return self.get_on_demand__group(pk_id=_id, action=_action)
                if _type == '3':
                    return self.get_on_demand__employee(pk_id=_id, action=_action)
            return {}
        raise exceptions.NotFound()

    @swagger_auto_schema(operation_summary='Org Chart Company')
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        self.default_group_filter = {'company_id': request.user.company_current_id}
        result = self.parse_params(params_dict=request.query_params.dict())
        return ResponseController.success_200(data=result, key_data='result')
