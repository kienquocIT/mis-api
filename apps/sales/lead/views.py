from django.db.models import OuterRef, Prefetch
from drf_yasg.utils import swagger_auto_schema

from apps.sales.opportunity.models import OpportunityCallLog
from apps.shared.extends.exceptions import handle_exception_all_view
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.lead.models import Lead, LeadStage, LeadChartInformation, LeadOpportunity, LeadCall, LeadMeeting, \
    LeadEmail
from apps.sales.lead.serializers import (
    LeadListSerializer, LeadCreateSerializer, LeadDetailSerializer, LeadUpdateSerializer,
    LeadStageListSerializer, LeadChartListSerializer, LeadListForOpportunitySerializer, LeadCallCreateSerializer,
    LeadCallDetailSerializer, LeadActivityListSerializer, LeadEmailCreateSerializer, LeadEmailDetailSerializer,
    LeadMeetingCreateSerializer, LeadMeetingDetailSerializer, LeadCallUpdateSerializer
)


__all__ = [
    'LeadList',
    'LeadDetail',
    'LeadStageList',
    'LeadChartList',
    'LeadListForOpportunity',
    'LeadCallList'
]


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
            request.data['title'] = self.get_object().title
        if all(['convert_opp' in request.data, 'map_opp' in request.data]):
            self.ser_context = {
                'convert_opp': True,
                'opp_mapped_id': request.data.get('opp_mapped_id')
            }
            request.data['title'] = self.get_object().title
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


class LeadCallList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityCallLog.objects
    serializer_create = LeadCallCreateSerializer
    serializer_detail = LeadCallDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Create Lead Call",
        operation_description="Create new Lead Call",
        request_body=LeadCallCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LeadCallDetail(BaseUpdateMixin):
    queryset = LeadCall.objects
    serializer_update = LeadCallUpdateSerializer
    serializer_detail = LeadCallDetailSerializer
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Update lead call",
        operation_description="Update lead call",
        request_body=LeadCallUpdateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code="edit"
    )
    def put(self, request, *args, pk, **kwargs):
        return self.update(request, *args, pk, **kwargs)


class LeadEmailList(BaseListMixin, BaseCreateMixin):
    queryset = LeadEmail.objects
    serializer_create = LeadEmailCreateSerializer
    serializer_detail = LeadEmailDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Create Lead Email",
        operation_description="Create new Lead Email",
        request_body=LeadEmailCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_current': request.user.employee_current,
        }
        return self.create(request, *args, **kwargs)


class LeadMeetingList(BaseListMixin, BaseCreateMixin):
    queryset = LeadMeeting.objects
    serializer_create = LeadMeetingCreateSerializer
    serializer_detail = LeadMeetingDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(
        operation_summary="Create Lead Meeting",
        operation_description="Create new Lead Meeting",
        request_body=LeadMeetingCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='create',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LeadActivityList(BaseRetrieveMixin):
    queryset = Lead.objects
    serializer_detail = LeadActivityListSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related('lead_call_lead', 'lead_meeting_lead', 'lead_email_lead')

    @swagger_auto_schema(operation_summary='Lead Activity List')
    @mask_view(
        login_require=True, auth_require=True,
        label_code='lead', model_code='lead', perm_code='view',
    )
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)




