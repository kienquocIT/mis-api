from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Periods
from apps.sales.revenue_plan.models import RevenuePlan, RevenuePlanGroupEmployee
from apps.sales.revenue_plan.serializers import (
    RevenuePlanListSerializer, RevenuePlanCreateSerializer,
    RevenuePlanDetailSerializer, RevenuePlanUpdateSerializer, RevenuePlanByReportPermListSerializer
)
from apps.shared import (
    BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin,
)


class RevenuePlanList(BaseListMixin, BaseCreateMixin):
    queryset = RevenuePlan.objects
    search_fields = [
        'code',
        'title',
        'date_created'
    ]
    serializer_list = RevenuePlanListSerializer
    serializer_create = RevenuePlanCreateSerializer
    serializer_detail = RevenuePlanDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'period_mapped',
            'employee_created'
        ).prefetch_related(
            'revenue_plan_mapped_group__group_mapped'
        )

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
        self.ser_context = {
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
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
        self.ser_context = {
            'company_id': request.user.company_current_id,
            'tenant_id': request.user.tenant_current_id,
        }
        return self.update(request, *args, **kwargs)


class RevenuePlanByReportPermList(BaseListMixin):
    queryset = RevenuePlanGroupEmployee.objects
    search_fields = [
        'code',
        'title',
        'date_created'
    ]
    serializer_list = RevenuePlanByReportPermListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        tenant_id = self.request.user.tenant_current_id
        company_id = self.request.user.company_current_id
        filters = {}
        if 'fiscal_year' not in self.request.query_params:
            this_period = Periods.get_current_period(tenant_id, company_id)
            if this_period:
                filters['revenue_plan_mapped__period_mapped_id'] = this_period.id
                if 'myself' in self.request.query_params:
                    filters['employee_mapped_id'] = self.request.user.employee_current_id
                return super().get_queryset().filter(**filters).select_related(
                    'employee_mapped','revenue_plan_mapped'
                ).prefetch_related(
                    'revenue_plan_mapped__period_mapped'
                )
        period = Periods.objects.filter(
            tenant_id=tenant_id, company_id=company_id,
            fiscal_year=self.request.query_params.get('fiscal_year')
        ).first()
        if period:
            filters['revenue_plan_mapped__period_mapped_id'] = period.id
            if 'myself' in self.request.query_params:
                filters['employee_mapped_id'] = self.request.user.employee_current_id
            return super().get_queryset().filter(**filters).select_related(
                'employee_mapped', 'revenue_plan_mapped'
            ).prefetch_related(
                'revenue_plan_mapped__period_mapped'
            )
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="RevenuePlan By Report Perm List",
        operation_description="Get RevenuePlan By Report Perm List",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='revenue_plan', model_code='revenueplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
