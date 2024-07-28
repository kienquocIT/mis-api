import json
from drf_yasg.utils import swagger_auto_schema
from apps.core.hr.models import Group
from apps.sales.budgetplan.models import BudgetPlan, BudgetPlanGroup, BudgetPlanGroupConfig, \
    EmployeeCanViewCompanyBudgetPlan, EmployeeCanLockBudgetPlan
from apps.sales.budgetplan.serializers import (
    BudgetPlanListSerializer, BudgetPlanCreateSerializer,
    BudgetPlanDetailSerializer, BudgetPlanUpdateSerializer, BudgetPlanGroupConfigListSerializer,
    BudgetPlanGroupConfigDetailSerializer, BudgetPlanGroupConfigCreateSerializer,
    ListCanViewCompanyBudgetPlanSerializer, ListCanLockBudgetPlanSerializer
)
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin,
)


class BudgetPlanList(BaseListMixin, BaseCreateMixin):
    queryset = BudgetPlan.objects
    search_fields = [
        'code',
        'title',
        'date_created'
    ]
    serializer_list = BudgetPlanListSerializer
    serializer_create = BudgetPlanCreateSerializer
    serializer_detail = BudgetPlanDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'period_mapped',
            'employee_created'
        ).prefetch_related()

    @swagger_auto_schema(
        operation_summary="BudgetPlan List",
        operation_description="Get BudgetPlan List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='budget_plan', model_code='budgetplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create BudgetPlan",
        operation_description="Create new BudgetPlan",
        request_body=BudgetPlanCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='budget_plan', model_code='budgetplan', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BudgetPlanDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = BudgetPlan.objects
    serializer_detail = BudgetPlanDetailSerializer
    serializer_update = BudgetPlanUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'period_mapped',
        ).prefetch_related(
            'budget_plan_group_budget_plan__group_mapped',
            'budget_plan_group_budget_plan__budget_plan_group_expense_budget_plan_group__expense_item',
            'budget_plan_company_expense_budget_plan__expense_item'
        )

    @classmethod
    def update_record_with_data_params(cls, budget_plan_id, query_params):
        if 'update_group' in query_params:
            obj = BudgetPlan.objects.filter(id=budget_plan_id).first()
            if obj:
                all_company_group = list(Group.objects.filter(
                    company_id=obj.company_id, tenant_id=obj.tenant_id, is_delete=False
                ).values_list('id', flat=True))
                all_budget_plan_group = list(obj.budget_plan_group_budget_plan.all().values_list(
                    'group_mapped_id', flat=True
                ))

                bulk_info = []
                for group_added_id in list(set(all_company_group).symmetric_difference(set(all_budget_plan_group))):
                    bulk_info.append(BudgetPlanGroup(budget_plan=obj, group_mapped_id=group_added_id))
                BudgetPlanGroup.objects.bulk_create(bulk_info)
        if 'lock_this_plan' in query_params:
            BudgetPlan.objects.filter(id=budget_plan_id).update(is_lock=True)
        if 'unlock_this_plan' in query_params:
            BudgetPlan.objects.filter(id=budget_plan_id).update(is_lock=False)
        return True

    @swagger_auto_schema(
        operation_summary="BudgetPlan detail",
        operation_description="Get BudgetPlan detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='budget_plan', model_code='budgetplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_current_id': request.user.employee_current_id,
            'company_current_id': request.user.company_current_id,
        }
        self.update_record_with_data_params(kwargs['pk'], request.query_params)
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update BudgetPlan",
        operation_description="Update BudgetPlan by ID",
        request_body=BudgetPlanUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='budget_plan', model_code='budgetplan', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_current_id': request.user.employee_current_id,
        }
        return self.update(request, *args, **kwargs)


class BudgetPlanGroupConfigList(BaseListMixin, BaseCreateMixin):
    queryset = BudgetPlanGroupConfig.objects
    search_fields = []
    serializer_list = BudgetPlanGroupConfigListSerializer
    serializer_create = BudgetPlanGroupConfigCreateSerializer
    serializer_detail = BudgetPlanGroupConfigDetailSerializer
    list_hidden_field = ['company_id']
    create_hidden_field = ['company_id']

    def get_queryset(self):
        return super().get_queryset().select_related('employee_allowed').prefetch_related()

    @classmethod
    def update_record_with_data_params(cls, company_current, query_params):
        delete_employee_allowed_id = query_params.get('delete_employee_allowed_id')
        if delete_employee_allowed_id:
            BudgetPlanGroupConfig.objects.filter(
                company=company_current, employee_allowed_id=delete_employee_allowed_id
            ).delete()
        if 'emp_id_can_view_company_bp' in query_params:
            bulk_info = []
            for emp_id in json.loads(query_params.get('emp_id_can_view_company_bp')):
                bulk_info.append(
                    EmployeeCanViewCompanyBudgetPlan(
                        company=company_current, employee_allowed_id=emp_id, can_view_company=True
                    )
                )
            EmployeeCanViewCompanyBudgetPlan.objects.filter(company=company_current).delete()
            EmployeeCanViewCompanyBudgetPlan.objects.bulk_create(bulk_info)
        if 'emp_id_can_lock_bp' in query_params:
            bulk_info = []
            for emp_id in json.loads(query_params.get('emp_id_can_lock_bp')):
                bulk_info.append(
                    EmployeeCanLockBudgetPlan(
                        company=company_current, employee_allowed_id=emp_id, can_lock_plan=True
                    )
                )
            EmployeeCanLockBudgetPlan.objects.filter(company=company_current).delete()
            EmployeeCanLockBudgetPlan.objects.bulk_create(bulk_info)
        return True

    @swagger_auto_schema(
        operation_summary="Budget Plan Config List",
        operation_description="Get Budget Plan Config List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        self.update_record_with_data_params(request.user.company_current, request.query_params)
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create BudgetPlan",
        operation_description="Create new BudgetPlan",
        request_body=BudgetPlanCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListCanViewCompanyBudgetPlan(BaseListMixin):
    queryset = EmployeeCanViewCompanyBudgetPlan.objects
    search_fields = []
    serializer_list = ListCanViewCompanyBudgetPlanSerializer
    list_hidden_field = ['company_id']

    def get_queryset(self):
        return super().get_queryset().filter(can_view_company=True).select_related(
            'employee_allowed'
        ).prefetch_related()

    @swagger_auto_schema(
        operation_summary="List Can View Company BudgetPlan",
        operation_description="Get List Can View Company Budget Plan",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListCanLockBudgetPlan(BaseListMixin):
    queryset = EmployeeCanLockBudgetPlan.objects
    search_fields = []
    serializer_list = ListCanLockBudgetPlanSerializer
    list_hidden_field = ['company_id']

    def get_queryset(self):
        return super().get_queryset().filter(can_lock_plan=True).select_related(
            'employee_allowed'
        ).prefetch_related()

    @swagger_auto_schema(
        operation_summary="List Can Lock BudgetPlan",
        operation_description="Get List Can Lock Budget Plan",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
