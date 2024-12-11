from drf_yasg.utils import swagger_auto_schema
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.lead.models import Lead, LeadStage, LeadChartInformation, LeadOpportunity
from apps.sales.lead.serializers import (
    LeadListSerializer, LeadCreateSerializer, LeadDetailSerializer, LeadUpdateSerializer,
    LeadStageListSerializer, LeadChartListSerializer, LeadListForOpportunitySerializer
)

__all__ = [
    'LeadList',
    'LeadDetail',
    'LeadStageList',
    'LeadChartList',
    'LeadListForOpportunity'
]

from apps.shared.extends.exceptions import handle_exception_all_view


class LeadList(BaseListMixin, BaseCreateMixin):
    queryset = Lead.objects
    search_fields = ['title', 'contact_name']
    serializer_list = LeadListSerializer
    serializer_create = LeadCreateSerializer
    serializer_detail = LeadDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        main_queryset = super().get_queryset().select_related('current_lead_stage').prefetch_related()
        return self.get_queryset_custom_direct_page(main_queryset)

    @swagger_auto_schema(
        operation_summary="Lead list",
        operation_description="Lead list",
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        try:
            LeadChartInformation.create_update_chart_information(
                self.request.user.tenant_current_id,
                self.request.user.company_current_id
            )
        except Exception as err:
            handle_exception_all_view(err, self)
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Lead",
        operation_description="Create new Lead",
        request_body=LeadCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LeadDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Lead.objects  # noqa
    serializer_list = LeadListSerializer
    serializer_create = LeadCreateSerializer
    serializer_detail = LeadDetailSerializer
    serializer_update = LeadUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'industry',
            'assign_to_sale',
            'current_lead_stage'
        ).prefetch_related(
            'lead_notes',
            'lead_configs__account_mapped',
            'lead_configs__assign_to_sale_config',
            'lead_configs__contact_mapped',
            'lead_configs__opp_mapped',
        )

    @swagger_auto_schema(operation_summary='Detail Lead')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Lead", request_body=LeadUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='edit',
    )
    def put(self, request, *args, **kwargs):
        if 'goto_stage' in request.data:
            self.ser_context = {'goto_stage': True}
        if all(['convert_opp' in request.data, 'map_opp' in request.data]):
            self.ser_context = {
                'convert_opp': True,
                'opp_mapped_id': request.data.get('opp_mapped_id')
            }
        return self.update(request, *args, **kwargs)


class LeadStageList(BaseListMixin):
    queryset = LeadStage.objects
    serializer_list = LeadStageListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Lead stage list",
        operation_description="Lead stage list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LeadChartList(BaseListMixin):
    queryset = LeadChartInformation.objects
    serializer_list = LeadChartListSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Lead stage list",
        operation_description="Lead stage list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LeadListForOpportunity(BaseListMixin):
    queryset = LeadOpportunity.objects
    search_fields = ['lead__title']
    serializer_list = LeadListForOpportunitySerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        if 'opp_id' in self.request.query_params:
            return super().get_queryset().filter(
                opportunity=self.request.query_params['opp_id']
            ).prefetch_related().select_related()
        return super().get_queryset().none()

    @swagger_auto_schema(
        operation_summary="Lead list",
        operation_description="Lead list",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='lead', model_code='lead', perm_code='view',
    )
    def get(self, request, *args, **kwargs):
        LeadChartInformation.create_update_chart_information(
            self.request.user.tenant_current_id, self.request.user.company_current_id
        )
        return self.list(request, *args, **kwargs)
