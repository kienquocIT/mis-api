from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel


MEETING_APP = [
    (0, _('Zoom')),
    (1, _('Google meet')),
    (2, _('Bflow meeting'))
]


# Create your models here.
class MeetingRoom(MasterDataAbstractModel):
    location = models.CharField(max_length=150)
    description = models.CharField(max_length=250, null=True)

    class Meta:
        verbose_name = 'Meeting Room'
        verbose_name_plural = 'Meeting Rooms'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MeetingZoomConfig(MasterDataAbstractModel):
    account_email = models.CharField(max_length=100)
    account_id = models.TextField(blank=True)
    client_id = models.TextField(blank=True)
    client_secret = models.TextField(blank=True)
    personal_meeting_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Meeting Zoom Config'
        verbose_name_plural = 'Meeting Zoom Configs'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MeetingSchedule(DataAbstractModel):
    meeting_content = models.CharField(null=True, max_length=250)
    meeting_type = models.BooleanField(default=False)  # false is online, true is offline
    meeting_room_mapped = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, null=True)
    meeting_start_date = models.DateField()
    meeting_start_time = models.TimeField()
    meeting_duration = models.FloatField()  # minute

    class Meta:
        verbose_name = 'Meeting Schedule'
        verbose_name_plural = 'Meetings Schedule'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MeetingScheduleParticipant(SimpleAbstractModel):
    meeting_schedule_mapped = models.ForeignKey(
        MeetingSchedule, on_delete=models.CASCADE, related_name='meeting_schedule_mapped'
    )
    participant = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)
    is_external = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Meeting Schedule Participant'
        verbose_name_plural = 'Meetings Schedule Participants'
        ordering = ()
        default_permissions = ()
        permissions = ()


class MeetingScheduleOnlineMeeting(DataAbstractModel):
    meeting_online_schedule_mapped = models.ForeignKey(
        MeetingSchedule, on_delete=models.CASCADE, related_name='meeting_online_schedule_mapped'
    )
    meeting_app = models.SmallIntegerField(choices=MEETING_APP, default=0)
    meeting_topic = models.CharField(max_length=250)
    meeting_recurring = models.BooleanField(default=False)
    meeting_recurring_data = models.JSONField(default=list)
    meeting_timezone_text = models.CharField(max_length=50)
    meeting_enable_continuous_meeting_chat = models.BooleanField(default=True)
    meeting_ID_type = models.BooleanField(default=False)  # False is autogen, True is get PMI
    meeting_ID = models.CharField(max_length=100, null=True)
    meeting_link = models.URLField(null=True)
    meeting_passcode = models.CharField(null=True, max_length=100)
    meeting_waiting_room = models.CharField(null=True, max_length=100)
    meeting_create_payload = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Meeting Schedule Online Meeting'
        verbose_name_plural = 'Meetings Schedule Online Meeting'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
