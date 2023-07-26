from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.sales.opportunity.models import OpportunityCallLog, OpportunityEmail, OpportunityMeeting, OpportunityDocument
from apps.sales.opportunity.serializers import (
    OpportunityCallLogListSerializer, OpportunityCallLogCreateSerializer,
    OpportunityCallLogDetailSerializer,
    OpportunityEmailListSerializer, OpportunityEmailCreateSerializer,
    OpportunityEmailDetailSerializer,
    OpportunityMeetingListSerializer, OpportunityMeetingCreateSerializer,
    OpportunityMeetingDetailSerializer, OpportunityDocumentListSerializer,
    OpportunityDocumentCreateSerializer, OpportunityDocumentDetailSerializer
)
from apps.shared import BaseListMixin, mask_view, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin, BaseDestroyMixin


class OpportunityCallLogList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
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


class OpportunityCallLogDelete(BaseDestroyMixin):
    queryset = OpportunityCallLog.objects

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Call Log List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


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


class OpportunityEmailDelete(BaseDestroyMixin):
    queryset = OpportunityEmail.objects

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Email List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OpportunityMeetingList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityMeeting.objects

    serializer_list = OpportunityMeetingListSerializer
    serializer_create = OpportunityMeetingCreateSerializer
    serializer_detail = OpportunityMeetingDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("opportunity").prefetch_related(
            'employee_attended_list',
            'customer_member_list'
        )

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


class OpportunityMeetingDelete(BaseDestroyMixin):
    queryset = OpportunityMeeting.objects

    @swagger_auto_schema(
        operation_summary="Delete Opportunity Meeting List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class OpportunityDocumentList(BaseListMixin, BaseCreateMixin):
    permission_classes = [IsAuthenticated] # noqa
    queryset = OpportunityDocument.objects

    serializer_list = OpportunityDocumentListSerializer
    serializer_create = OpportunityDocumentCreateSerializer
    serializer_detail = OpportunityDocumentDetailSerializer

    def get_queryset(self):
        return super().get_queryset().select_related(
            'opportunity'
        )

    @swagger_auto_schema(
        operation_summary="OpportunityDocument List",
        operation_description="Get OpportunityDocument List",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create OpportunityDocument",
        operation_description="Create new OpportunityDocument",
        request_body=OpportunityMeetingCreateSerializer,
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def post(self, request, *args, **kwargs):
        self.ser_context = {
            'user': request.user
        }
        return self.create(request, *args, **kwargs)


class OpportunityDocumentDetail(BaseRetrieveMixin, BaseUpdateMixin,):
    permission_classes = [IsAuthenticated]
    queryset = OpportunityDocument.objects
    serializer_detail = OpportunityDocumentDetailSerializer

    @swagger_auto_schema(
        operation_summary="OpportunityDocument detail",
        operation_description="Get OpportunityDocument detail by ID",
    )
    @mask_view(login_require=True, auth_require=True, code_perm='')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
