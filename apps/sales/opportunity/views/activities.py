from drf_yasg.utils import swagger_auto_schema

from apps.sales.opportunity.models import OpportunityCallLog, OpportunityEmail, OpportunityMeeting, \
    OpportunityDocument, OpportunityActivityLogs
from apps.sales.opportunity.serializers import (
    OpportunityCallLogListSerializer, OpportunityCallLogCreateSerializer,
    OpportunityCallLogDetailSerializer, OpportunityCallLogUpdateSerializer,
    OpportunityEmailListSerializer, OpportunityEmailCreateSerializer,
    OpportunityEmailDetailSerializer, OpportunityEmailUpdateSerializer,
    OpportunityMeetingListSerializer, OpportunityMeetingCreateSerializer,
    OpportunityMeetingDetailSerializer, OpportunityMeetingUpdateSerializer,
    OpportunityDocumentListSerializer, OpportunityDocumentCreateSerializer,
    OpportunityDocumentDetailSerializer, OpportunityActivityLogsListSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin
from ..filters import OpportunityMeetingFilters


class OpportunityCallLogList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityCallLog.objects

    serializer_list = OpportunityCallLogListSerializer
    serializer_create = OpportunityCallLogCreateSerializer
    serializer_detail = OpportunityCallLogDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity__customer", "contact")

    @swagger_auto_schema(
        operation_summary="OpportunityCallLog List",
        operation_description="Get OpportunityCallLog List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityCallLog",
        operation_description="Create new OpportunityCallLog",
        request_body=OpportunityCallLogCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_id': request.user.employee_current_id,
        }
        return self.create(request, *args, **kwargs)


class OpportunityCallLogDetail(BaseRetrieveMixin, BaseUpdateMixin, ):
    queryset = OpportunityCallLog.objects
    serializer_detail = OpportunityCallLogDetailSerializer
    serializer_update = OpportunityCallLogUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity__customer", "contact")

    @swagger_auto_schema(
        operation_summary="OpportunityCallLog detail",
        operation_description="Get OpportunityCallLog detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Opportunity Call Log",
        operation_description="Update Opportunity Call Log by ID",
        request_body=OpportunityCallLogUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityEmailList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityEmail.objects

    serializer_list = OpportunityEmailListSerializer
    serializer_create = OpportunityEmailCreateSerializer
    serializer_detail = OpportunityEmailDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity")

    @swagger_auto_schema(
        operation_summary="OpportunityEmail List",
        operation_description="Get OpportunityEmail List",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityEmail",
        operation_description="Create new OpportunityEmail",
        request_body=OpportunityEmailCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_id': request.user.employee_current_id,
            'tenant_id': request.user.tenant_current_id,
            'company_id': request.user.company_current_id
        }
        return self.create(request, *args, **kwargs)


class OpportunityEmailDetail(BaseRetrieveMixin, BaseUpdateMixin, ):
    queryset = OpportunityEmail.objects
    serializer_detail = OpportunityEmailDetailSerializer
    serializer_update = OpportunityEmailUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity")

    @swagger_auto_schema(
        operation_summary="OpportunityEmail detail",
        operation_description="Get OpportunityEmail detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update Opportunity Email",
        operation_description="Update Opportunity Email by ID",
        request_body=OpportunityEmailUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityMeetingList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityMeeting.objects
    serializer_list = OpportunityMeetingListSerializer
    serializer_create = OpportunityMeetingCreateSerializer
    serializer_detail = OpportunityMeetingDetailSerializer
    filterset_class = OpportunityMeetingFilters

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity").prefetch_related(
            'employee_attended_list',
            'customer_member_list',
            'opportunity__employee_inherit'
        )

    @swagger_auto_schema(
        operation_summary="OpportunityMeeting List",
        operation_description="Get OpportunityMeeting List",
    )
    @mask_view(
        login_require=True, auth_require=False,
        # label_code='opportunity', model_code='opportunity', perm_code="view"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityMeeting",
        operation_description="Create new OpportunityMeeting",
        request_body=OpportunityMeetingCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'employee_id': request.user.employee_current_id,
        }
        return self.create(request, *args, **kwargs)


class OpportunityMeetingDetail(BaseRetrieveMixin, BaseUpdateMixin, ):
    queryset = OpportunityMeeting.objects
    serializer_detail = OpportunityMeetingDetailSerializer
    serializer_update = OpportunityMeetingUpdateSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity")

    @swagger_auto_schema(
        operation_summary="Opportunity Meeting detail",
        operation_description="Get Opportunity Meeting detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Meeting",
        operation_description="Update Opportunity Meeting by ID",
        request_body=OpportunityMeetingUpdateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityDocumentList(BaseListMixin, BaseCreateMixin):
    queryset = OpportunityDocument.objects

    serializer_list = OpportunityDocumentListSerializer
    serializer_create = OpportunityDocumentCreateSerializer
    serializer_detail = OpportunityDocumentDetailSerializer

    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related(
            'opportunity',
        )

    @swagger_auto_schema(
        operation_summary="OpportunityDocument List",
        operation_description="Get OpportunityDocument List",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityDocument",
        operation_description="Create new OpportunityDocument",
        request_body=OpportunityMeetingCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.create(request, *args, **kwargs)


class OpportunityDocumentDetail(BaseRetrieveMixin, BaseUpdateMixin, ):
    queryset = OpportunityDocument.objects
    serializer_detail = OpportunityDocumentDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity")

    @swagger_auto_schema(
        operation_summary="OpportunityDocument detail",
        operation_description="Get OpportunityDocument detail by ID",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OpportunityActivityLogList(BaseListMixin):
    queryset = OpportunityActivityLogs.objects
    serializer_list = OpportunityActivityLogsListSerializer
    filterset_fields = {
        'opportunity': ['exact'],
    }

    def get_queryset(self):
        return super().get_queryset().select_related("task", "call", "meeting", "document", "email")

    @swagger_auto_schema(
        operation_summary="Opportunity activity logs list",
        operation_description="Opportunity activity logs list",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
