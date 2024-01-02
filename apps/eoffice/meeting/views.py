from drf_yasg.utils import swagger_auto_schema
from apps.eoffice.meeting.models import MeetingRoom, MeetingZoomConfig, MeetingSchedule
from apps.eoffice.meeting.serializers import (
    MeetingRoomListSerializer, MeetingRoomDetailSerializer,
    MeetingRoomUpdateSerializer, MeetingRoomCreateSerializer,
    MeetingZoomConfigListSerializer, MeetingZoomConfigDetailSerializer,
    MeetingZoomConfigCreateSerializer, MeetingScheduleListSerializer,
    MeetingScheduleCreateSerializer, MeetingScheduleDetailSerializer, MeetingScheduleUpdateSerializer,
)
from apps.shared import mask_view, BaseListMixin, BaseCreateMixin, BaseRetrieveMixin, BaseUpdateMixin


# Create your views here.
class MeetingRoomList(BaseListMixin, BaseCreateMixin):
    queryset = MeetingRoom.objects
    serializer_list = MeetingRoomListSerializer
    serializer_create = MeetingRoomCreateSerializer

    serializer_detail = MeetingRoomDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Meeting Room list",
        operation_description="Meeting Room list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Meeting Room",
        operation_description="Create new Meeting Room",
        request_body=MeetingRoomCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MeetingRoomDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = MeetingRoom.objects
    serializer_list = MeetingRoomListSerializer
    serializer_create = MeetingRoomCreateSerializer
    serializer_detail = MeetingRoomDetailSerializer
    serializer_update = MeetingRoomUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Meeting Room')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Meeting Room", request_body=MeetingRoomUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MeetingZoomConfigList(BaseListMixin, BaseCreateMixin):
    queryset = MeetingZoomConfig.objects
    serializer_list = MeetingZoomConfigListSerializer
    serializer_create = MeetingZoomConfigCreateSerializer

    serializer_detail = MeetingZoomConfigDetailSerializer
    list_hidden_field = BaseListMixin.LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(
        operation_summary="Meeting Zoom Config list",
        operation_description="Meeting Zoom Config list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Meeting Zoom Config",
        operation_description="Create new Meeting Zoom Config",
        request_body=MeetingZoomConfigCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MeetingZoomConfigDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = MeetingZoomConfig.objects
    serializer_list = MeetingZoomConfigListSerializer
    serializer_create = MeetingZoomConfigCreateSerializer
    serializer_detail = MeetingZoomConfigDetailSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Meeting Zoom Config')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class MeetingScheduleList(BaseListMixin, BaseCreateMixin):
    queryset = MeetingSchedule.objects
    serializer_list = MeetingScheduleListSerializer
    serializer_create = MeetingScheduleCreateSerializer

    serializer_detail = MeetingScheduleDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @swagger_auto_schema(
        operation_summary="Meeting Schedule list",
        operation_description="Meeting Schedule list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Meeting Schedule",
        operation_description="Create new Meeting Schedule",
        request_body=MeetingScheduleCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MeetingScheduleDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = MeetingSchedule.objects
    serializer_list = MeetingScheduleListSerializer
    serializer_create = MeetingScheduleCreateSerializer
    serializer_detail = MeetingScheduleDetailSerializer
    serializer_update = MeetingScheduleUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    @swagger_auto_schema(operation_summary='Detail Meeting Schedule')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update Meeting Schedule", request_body=MeetingScheduleUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=True,
        allow_admin_tenant=True, allow_admin_company=True,
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
