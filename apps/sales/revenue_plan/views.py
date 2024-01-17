from drf_yasg.utils import swagger_auto_schema
from apps.sales.revenue_plan.models import RevenuePlan
from apps.sales.revenue_plan.serializers import (
    RevenuePlanListSerializer, RevenuePlanCreateSerializer,
    RevenuePlanDetailSerializer, RevenuePlanUpdateSerializer
)
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin,
)


class RevenuePlanList(BaseListMixin, BaseCreateMixin):
    queryset = RevenuePlan.objects
    serializer_list = RevenuePlanListSerializer
    serializer_create = RevenuePlanCreateSerializer
    serializer_detail = RevenuePlanListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'period_mapped',
            'employee_created'
        ).prefetch_related()

    @swagger_auto_schema(
        operation_summary="RevenuePlan List",
        operation_description="Get RevenuePlan List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='revenue_plan', model_code='revenueplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create RevenuePlan",
        operation_description="Create new RevenuePlan",
        request_body=RevenuePlanCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='revenue_plan', model_code='revenueplan', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RevenuePlanDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = RevenuePlan.objects
    serializer_detail = RevenuePlanDetailSerializer
    serializer_update = RevenuePlanUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related('period_mapped').prefetch_related(
            'revenue_plan_mapped_group__group_mapped',
            'revenue_plan_mapped_group_employee__employee_mapped'
        )

    @swagger_auto_schema(
        operation_summary="RevenuePlan detail",
        operation_description="Get RevenuePlan detail by ID",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='revenue_plan', model_code='revenueplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update RevenuePlan",
        operation_description="Update RevenuePlan by ID",
        request_body=RevenuePlanUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='revenue_plan', model_code='revenueplan', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
