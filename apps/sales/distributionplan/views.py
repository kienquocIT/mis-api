from drf_yasg.utils import swagger_auto_schema
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.distributionplan.models import DistributionPlan
from apps.sales.distributionplan.serializers import (
    DistributionPlanListSerializer, DistributionPlanDetailSerializer,
    DistributionPlanCreateSerializer, DistributionPlanUpdateSerializer,
)

__all__ = [
    'DistributionPlanList',
    'DistributionPlanDetail',
]


class DistributionPlanList(BaseListMixin, BaseCreateMixin):
    queryset = DistributionPlan.objects
    search_fields = [
        'title',
        'code',
    ]
    filterset_fields = {
        'system_status': ['exact'],
    }
    serializer_list = DistributionPlanListSerializer
    serializer_create = DistributionPlanCreateSerializer
    serializer_detail = DistributionPlanDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = CREATE_HIDDEN_FIELD_DEFAULT = [
        'tenant_id', 'company_id',
        'employee_created_id', 'employee_inherit_id',
    ]

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Distribution Plan list",
        operation_description="Distribution Plan list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='distributionplan', model_code='distributionplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Distribution Plan",
        operation_description="Create new Distribution Plan",
        request_body=DistributionPlanCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='distributionplan', model_code='distributionplan', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DistributionPlanDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = DistributionPlan.objects  # noqa
    serializer_list = DistributionPlanListSerializer
    serializer_create = DistributionPlanCreateSerializer
    serializer_detail = DistributionPlanDetailSerializer
    serializer_update = DistributionPlanUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail Distribution Plan')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='distributionplan', model_code='distributionplan', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Distribution Plan",
        request_body=DistributionPlanUpdateSerializer
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='distributionplan', model_code='distributionplan', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = DistributionPlanUpdateSerializer
        return self.update(request, *args, **kwargs)
