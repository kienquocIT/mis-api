from django.urls import path
from apps.eoffice.meeting.views import (
    MeetingRoomList, MeetingRoomDetail, MeetingZoomConfigList, MeetingZoomConfigDetail,
    MeetingScheduleList, MeetingScheduleDetail
)

urlpatterns = [
    path('meetingrooms', MeetingRoomList.as_view(), name='MeetingRoomList'),
    path('meetingroom/<str:pk>', MeetingRoomDetail.as_view(), name='MeetingRoomDetail'),
    path('zoom-configs', MeetingZoomConfigList.as_view(), name='MeetingZoomConfigList'),
    path('zoom-config/<str:pk>', MeetingZoomConfigDetail.as_view(), name='MeetingZoomConfigDetail'),
    path('meetings-schedule', MeetingScheduleList.as_view(), name='MeetingScheduleList'),
    path('meeting-schedule/<str:pk>', MeetingScheduleDetail.as_view(), name='MeetingScheduleDetail')
]
