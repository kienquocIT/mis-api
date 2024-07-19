from drf_yasg.utils import swagger_auto_schema
from apps.sales.budgetplan.models import BudgetPlan
from apps.sales.budgetplan.serializers import (
    BudgetPlanListSerializer, BudgetPlanCreateSerializer,
    BudgetPlanDetailSerializer, BudgetPlanUpdateSerializer
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
        login_require=True, auth_require=False,
        # label_code='budget_plan', model_code='budgetplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create BudgetPlan",
        operation_description="Create new BudgetPlan",
        request_body=BudgetPlanCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='budget_plan', model_code='budgetplan', perm_code='create',
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
        return super().get_queryset().select_related('period_mapped').prefetch_related()

    @swagger_auto_schema(
        operation_summary="BudgetPlan detail",
        operation_description="Get BudgetPlan detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='budget_plan', model_code='budgetplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update BudgetPlan",
        operation_description="Update BudgetPlan by ID",
        request_body=BudgetPlanUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='budget_plan', model_code='budgetplan', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
