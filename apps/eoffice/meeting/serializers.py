from datetime import datetime, timedelta
from django.core.mail import get_connection, EmailMessage
import requests
from icalendar import Calendar, Event
from rest_framework import serializers
from apps.eoffice.meeting.models import (
    MeetingRoom, MeetingZoomConfig, MeetingSchedule, MeetingScheduleParticipant, MeetingScheduleOnlineMeeting
)
from apps.shared import MeetingScheduleMsg


# MeetingRoom
class MeetingRoomListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingRoom
        fields = (
            'id',
            'title',
            'code',
            'location',
            'description'
        )


class MeetingRoomCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    class Meta:
        model = MeetingRoom
        fields = (
            'title',
            'code',
            'location',
            'description'
        )

    @classmethod
    def validate_code(cls, value):
        if MeetingRoom.objects.filter_current(fill__company=True, fill__tenant=True, code=value).exists():
            raise serializers.ValidationError({'code': MeetingScheduleMsg.DUP_CODE})
        return value

    @classmethod
    def validate_description(cls, value):
        if not value:
            raise serializers.ValidationError({'description': MeetingScheduleMsg.DES_IS_REQUIRED})
        return value


class MeetingRoomDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingRoom
        fields = (
            'id',
            'title',
            'code',
            'location',
            'description'
        )


class MeetingRoomUpdateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True)

    class Meta:
        model = MeetingRoom
        fields = (
            'title',
            'location',
            'description'
        )

    @classmethod
    def validate_description(cls, value):
        if not value:
            raise serializers.ValidationError({'description': MeetingScheduleMsg.DES_IS_REQUIRED})
        return value


# Zoom config
class MeetingZoomConfigListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingZoomConfig
        fields = (
            'id',
            'account_email',
            'account_id',
            'client_id',
            'client_secret',
            'personal_meeting_id'
        )


class MeetingZoomConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingZoomConfig
        fields = (
            'account_email',
            'account_id',
            'client_id',
            'client_secret',
            'personal_meeting_id'
        )

    def create(self, validated_data):
        MeetingZoomConfig.objects.filter_current(
            fill__tenant=True, fill__company=True
        ).delete()
        zoom_config = MeetingZoomConfig.objects.create(**validated_data)
        return zoom_config


class MeetingZoomConfigDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingZoomConfig
        fields = (
            'id',
            'account_email',
            'account_id',
            'client_id',
            'client_secret',
            'personal_meeting_id'
        )


class MeetingZoomConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingZoomConfig
        fields = (
            'account_email',
            'account_id',
            'client_id',
            'client_secret',
            'personal_meeting_id'
        )


# Meeting schedule
class MeetingScheduleListSerializer(serializers.ModelSerializer):  # noqa
    date_occur = serializers.SerializerMethodField()

    class Meta:
        model = MeetingSchedule
        fields = (
            'id',
            'title',
            'meeting_content',
            'meeting_type',
            'meeting_start_date',
            'meeting_start_time',
            'meeting_duration',
            'date_occur'
        )

    @classmethod
    def get_date_occur(cls, obj):
        date = obj.meeting_start_date.strftime('%Y-%m-%d')
        time = obj.meeting_start_time.strftime('%H:%M')
        return date + ' ' + time + ' ' + ('AM' if time.split(':')[0] < '12' else 'PM')


def create_participants_mapped(meeting_schedule, participants_list):
    bulk_info = []
    for item in participants_list:
        bulk_info.append(
            MeetingScheduleParticipant(
                meeting_schedule_mapped=meeting_schedule,
                participant_id=item.get('participant_id'),
                is_external=item.get('is_external')
            )
        )
    MeetingScheduleParticipant.objects.filter(meeting_schedule_mapped=meeting_schedule).delete()
    MeetingScheduleParticipant.objects.bulk_create(bulk_info)
    return True


def create_online_meeting_object(meeting_config, zoom_meeting_obj):
    payload = zoom_meeting_obj.meeting_create_payload
    config_obj = meeting_config.first()
    account_id = config_obj.account_id
    client_id = config_obj.client_id
    client_secret = config_obj.client_secret
    auth_token_url = "https://zoom.us/oauth/token"
    api_base_url = "https://api.zoom.us/v2"
    data = {
        "grant_type": "account_credentials",
        "account_id": account_id,
        "client_secret": client_secret
    }
    response = requests.post(auth_token_url, auth=(client_id, client_secret), data=data, timeout=60)

    if response.status_code != 200:
        raise serializers.ValidationError({'Online meeting': 'Unable to get access token'})
    response_data = response.json()
    access_token = response_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    resp = requests.post(f"{api_base_url}/users/me/meetings", headers=headers, json=payload, timeout=60)
    if resp.status_code != 201:
        raise serializers.ValidationError({'Online meeting': 'Unable to generate meeting link'})
    response_data = resp.json()

    zoom_meeting_obj.meeting_ID = response_data.get("pmi") if response_data.get("pmi") else response_data.get("id")
    zoom_meeting_obj.meeting_link = response_data.get("join_url")
    zoom_meeting_obj.meeting_passcode = response_data.get("password")
    zoom_meeting_obj.save(update_fields=["meeting_ID", "meeting_link", "meeting_passcode"])
    return response_data


def create_ics_calendar_meeting_file(meeting_id, meeting_topic, meeting_host_email, start_date, start_time, duration):
    start_date = start_date.strftime('%Y-%m-%d').split('-')
    start_time = start_time.strftime('%H:%M').split(':')
    dt_start_data = datetime(
        int(start_date[0]), int(start_date[1]), int(start_date[2]), int(start_time[0]), int(start_time[1]), 0
    )
    dt_start_end = dt_start_data + timedelta(minutes=duration)
    calendar = Calendar()
    event = Event()
    event.add('summary', meeting_topic)
    event.add('organizer', meeting_host_email)
    event.add('dtstart', dt_start_data)
    event.add('dtend', dt_start_end)
    calendar.add_component(event)
    try:
        file_path = f'apps/eoffice/meeting/calendar_ics_file/calendar_{meeting_id}.ics'
        with open(file_path, 'wb') as file:
            file.write(calendar.to_ical())
        return file_path
    except Exception as error:
        raise serializers.ValidationError({'Online meeting': f'Cannot create calendar file ({error})'})


def send_mail(meeting_schedule, response_data, meeting_time, date, time, duration):
    try:
        employee = meeting_schedule.employee_inherit
        company_name = meeting_schedule.company.title
        company_email = meeting_schedule.company.email
        company_email_app_password = meeting_schedule.company.email_app_password
        meeting_topic = response_data.get('topic')
        meeting_id = response_data.get('join_url').split('?')[0].split('/')[-1]
        meeting_url = response_data.get('join_url')
        meeting_passcode = response_data.get('password')
        email = EmailMessage(
            subject=meeting_topic,
            body=f"{employee.get_full_name(2)} from {company_name} has invited you to a scheduled Zoom meeting."
                 f"\n\nTopic: {meeting_topic}\nTime: {meeting_time}"
                 f"\n\nJoin Zoom Meeting\n{meeting_url}"
                 f"\n\nMeeting ID: {meeting_id}"
                 f"\nPasscode: {meeting_passcode}",
            from_email=company_email,
            to=[item.participant.email for item in meeting_schedule.meeting_schedule_mapped.all()],
            cc=[],
            bcc=[],
            reply_to=[],
        )
        path = create_ics_calendar_meeting_file(meeting_id, meeting_topic, employee.email, date, time, duration)
        for attachment in [path]:
            email.attach_file(attachment)
        connection = get_connection(
            username=company_email,
            password=company_email_app_password,
            fail_silently=False,
        )
        email.connection = connection
        email.send()
        return True
    except Exception as error:
        raise serializers.ValidationError({'Online meeting': f'Cannot send email ({error})'})


def after_create_online_meeting(meeting_schedule, online_meeting_data):
    MeetingScheduleOnlineMeeting.objects.filter(meeting_online_schedule_mapped=meeting_schedule).delete()
    zoom_meeting_obj = MeetingScheduleOnlineMeeting.objects.create(
        meeting_online_schedule_mapped=meeting_schedule,
        **online_meeting_data
    )
    meeting_config = MeetingZoomConfig.objects.filter_current(fill__tenant=True, fill__company=True)
    if meeting_config.exists():
        response_data = create_online_meeting_object(meeting_config, zoom_meeting_obj)
        duration = meeting_schedule.meeting_duration
        date = meeting_schedule.meeting_start_date
        time = meeting_schedule.meeting_start_time
        meeting_time = date.strftime('%Y-%m-%d') + ' ' + time.strftime('%H:%M') + ' ' + (
            'AM' if time.strftime('%H:%M').split(':')[0] < '12' else 'PM'
        )
        send_mail(meeting_schedule, response_data, meeting_time, date, time, duration)
    return True


def check_room_overlap(item, data):
    item_mt_time = f"{item.meeting_start_date} {item.meeting_start_time}"
    this_mt_time = f"{data.get('meeting_start_date')} {data.get('meeting_start_time')}"
    item_mt_datetime = datetime.strptime(item_mt_time, "%Y-%m-%d %H:%M:%S")
    this_mt_datetime = datetime.strptime(this_mt_time, "%Y-%m-%d %H:%M:%S")
    item_end_datetime = item_mt_datetime + timedelta(minutes=item.meeting_duration)
    this_end_datetime = this_mt_datetime + timedelta(minutes=data.get('meeting_duration'))
    return (item_mt_datetime < this_end_datetime) and (this_mt_datetime < item_end_datetime)


class MeetingScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'

    def validate(self, validate_data):
        if validate_data.get('meeting_type') is True:
            # check room
            all_offline_meeting = MeetingSchedule.objects.filter_current(
                fill__company=True,
                fill__tenant=True,
                meeting_type=True,
                meeting_room_mapped=validate_data.get('meeting_room_mapped')
            )
            for item in all_offline_meeting:
                if check_room_overlap(item, validate_data):
                    raise serializers.ValidationError({'room': MeetingScheduleMsg.ROOM_IS_NOT_AVAILABLE})
        return validate_data

    def create(self, validated_data):
        meeting_schedule = MeetingSchedule.objects.create(
            **validated_data, employee_inherit_id=validated_data['employee_created_id']
        )
        create_participants_mapped(meeting_schedule, self.initial_data.get('participants', []))
        if meeting_schedule.meeting_type is False:
            after_create_online_meeting(meeting_schedule, self.initial_data.get('online_meeting_data', {}))
        return meeting_schedule


class MeetingScheduleDetailSerializer(serializers.ModelSerializer):  # noqa
    participants = serializers.SerializerMethodField()
    meeting_room_mapped = serializers.SerializerMethodField()
    online_meeting_data = serializers.SerializerMethodField()

    class Meta:
        model = MeetingSchedule
        fields = (
            'id',
            'title',
            'meeting_content',
            'meeting_type',
            'meeting_room_mapped',
            'meeting_start_date',
            'meeting_start_time',
            'meeting_duration',
            'participants',
            'online_meeting_data'
        )

    @classmethod
    def get_participants(cls, obj):
        participants = [{
            'id': item.participant_id,
            'full_name': item.participant.get_full_name(2),
            'is_external': item.is_external,
        } for item in obj.meeting_schedule_mapped.all()]
        return participants

    @classmethod
    def get_meeting_room_mapped(cls, obj):
        return {
            'id': obj.meeting_room_mapped_id,
            'title': obj.meeting_room_mapped.title,
            'description': obj.meeting_room_mapped.description
        } if obj.meeting_room_mapped else None

    @classmethod
    def get_online_meeting_data(cls, obj):
        return [{
            'meeting_app': item.meeting_app,
            'meeting_topic': item.meeting_topic,
            'meeting_timezone_text': item.meeting_timezone_text,
            'meeting_ID': item.meeting_ID,
            'meeting_link': item.meeting_link,
            'meeting_passcode': item.meeting_passcode,
            'meeting_create_payload': item.meeting_create_payload
        } for item in obj.meeting_online_schedule_mapped.all()]


class MeetingScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'
