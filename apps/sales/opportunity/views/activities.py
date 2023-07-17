from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.sales.opportunity.models import OpportunityCallLog, OpportunityEmail, OpportunityMeeting
from apps.sales.opportunity.serializers import (
    OpportunityCallLogListSerializer, OpportunityCallLogCreateSerializer,
    OpportunityCallLogDetailSerializer, OpportunityCallLogDeleteSerializer,
    OpportunityEmailListSerializer, OpportunityEmailCreateSerializer,
    OpportunityEmailDetailSerializer, OpportunityEmailDeleteSerializer,
    OpportunityMeetingListSerializer, OpportunityMeetingCreateSerializer,
    OpportunityMeetingDetailSerializer, OpportunityMeetingDeleteSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


class OpportunityCallLogList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityCallLog.objects

    serializer_list = OpportunityCallLogListSerializer
    serializer_create = OpportunityCallLogCreateSerializer
    serializer_detail = OpportunityCallLogDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity", "contact")

    @swagger_auto_schema(
        operation_summary="OpportunityCallLog List",
        operation_description="Get OpportunityCallLog List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityCallLog",
        operation_description="Create new OpportunityCallLog",
        request_body=OpportunityCallLogCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityCallLogDetail(BaseRetrieveMixin, BaseUpdateMixin,):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityCallLog.objects
    serializer_detail = OpportunityCallLogDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity", "contact")

    @swagger_auto_schema(
        operation_summary="OpportunityCallLog detail",
        operation_description="Get OpportunityCallLog detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OpportunityCallLogDelete(BaseUpdateMixin):
    queryset = OpportunityCallLog.objects
    serializer_detail = OpportunityCallLogDetailSerializer
    serializer_update = OpportunityCallLogDeleteSerializer

    @swagger_auto_schema(operation_summary="Delete Opportunity Call Log List", request_body=OpportunityCallLogDeleteSerializer)
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityEmailList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityEmail.objects

    serializer_list = OpportunityEmailListSerializer
    serializer_create = OpportunityEmailCreateSerializer
    serializer_detail = OpportunityEmailDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity", "email_to_contact")

    @swagger_auto_schema(
        operation_summary="OpportunityEmail List",
        operation_description="Get OpportunityEmail List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityEmail",
        operation_description="Create new OpportunityEmail",
        request_body=OpportunityEmailCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityEmailDetail(BaseRetrieveMixin, BaseUpdateMixin,):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityEmail.objects
    serializer_detail = OpportunityEmailDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity", "email_to_contact")

    @swagger_auto_schema(
        operation_summary="OpportunityEmail detail",
        operation_description="Get OpportunityEmail detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OpportunityEmailDelete(BaseUpdateMixin):
    queryset = OpportunityEmail.objects
    serializer_detail = OpportunityEmailDetailSerializer
    serializer_update = OpportunityEmailDeleteSerializer

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Email List",
        request_body=OpportunityEmailDeleteSerializer
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class OpportunityMeetingList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityMeeting.objects

    serializer_list = OpportunityMeetingListSerializer
    serializer_create = OpportunityMeetingCreateSerializer
    serializer_detail = OpportunityMeetingDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity")

    @swagger_auto_schema(
        operation_summary="OpportunityMeeting List",
        operation_description="Get OpportunityMeeting List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityMeeting",
        operation_description="Create new OpportunityMeeting",
        request_body=OpportunityMeetingCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpportunityMeetingDetail(BaseRetrieveMixin, BaseUpdateMixin,):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityMeeting.objects
    serializer_detail = OpportunityMeetingDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity")

    @swagger_auto_schema(
        operation_summary="OpportunityMeeting detail",
        operation_description="Get OpportunityMeeting detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class OpportunityMeetingDelete(BaseUpdateMixin):
    queryset = OpportunityMeeting.objects
    serializer_detail = OpportunityMeetingDetailSerializer
    serializer_update = OpportunityMeetingDeleteSerializer

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Meeting List",
        request_body=OpportunityMeetingDeleteSerializer
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
