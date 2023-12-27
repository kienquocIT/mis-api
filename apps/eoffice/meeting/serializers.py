import requests
from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.meeting.models import (
    MeetingRoom, MeetingZoomConfig, MeetingSchedule, MeetingScheduleParticipant, MeetingScheduleOnlineMeeting
)


# MeetingRoom
class MeetingRoomListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingRoom
        fields = '__all__'


class MeetingRoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = '__all__'


class MeetingRoomDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingRoom
        fields = '__all__'


class MeetingRoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = '__all__'


# zoom config

class MeetingZoomConfigListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingZoomConfig
        fields = '__all__'


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
        fields = '__all__'


class MeetingZoomConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingZoomConfig
        fields = '__all__'


# meeting schedule

class MeetingScheduleListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingSchedule
        fields = '__all__'


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


def create_online_meeting_mapped(meeting_schedule, online_meeting_data):
    MeetingScheduleOnlineMeeting.objects.filter(meeting_online_schedule_mapped=meeting_schedule).delete()
    zoom_mt_obj = MeetingScheduleOnlineMeeting.objects.create(
        meeting_online_schedule_mapped=meeting_schedule,
        **online_meeting_data
    )
    payload = zoom_mt_obj.meeting_create_payload
    meeting_config_list = MeetingZoomConfig.objects.filter_current(fill__tenant=True, fill__company=True)
    if meeting_config_list.exists():
        meeting_config = meeting_config_list.first()
        account_id = meeting_config.account_id
        client_id = meeting_config.client_id
        client_secret = meeting_config.client_secret
        auth_token_url = "https://zoom.us/oauth/token"
        api_base_url = "https://api.zoom.us/v2"
        data = {
            "grant_type": "account_credentials",
            "account_id": account_id,
            "client_secret": client_secret
        }
        response = requests.post(auth_token_url, auth=(client_id, client_secret), data=data)

        if response.status_code != 200:
            raise serializers.ValidationError({'Online meeting': 'Unable to get access token'})
        response_data = response.json()
        access_token = response_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        resp = requests.post(f"{api_base_url}/users/me/meetings", headers=headers, json=payload)
        if resp.status_code != 201:
            raise serializers.ValidationError({'Online meeting': 'Unable to generate meeting link'})
        response_data = resp.json()
        zoom_mt_obj.meeting_ID = response_data.get("pmi") if response_data.get("pmi") else response_data.get("id")
        zoom_mt_obj.meeting_link = response_data.get("join_url")
        zoom_mt_obj.meeting_passcode = response_data.get("password")
        zoom_mt_obj.save()
    return True


class MeetingScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'

    def create(self, validated_data):
        meeting_schedule = MeetingSchedule.objects.create(**validated_data)
        create_participants_mapped(meeting_schedule, self.initial_data.get('participants', []))
        if meeting_schedule.meeting_type is False:
            create_online_meeting_mapped(meeting_schedule, self.initial_data.get('online_meeting_data', {}))
        return meeting_schedule


class MeetingScheduleDetailSerializer(serializers.ModelSerializer):  # noqa
    participants = serializers.SerializerMethodField()
    meeting_room_mapped = serializers.SerializerMethodField()
    online_meeting_data = serializers.SerializerMethodField()

    class Meta:
        model = MeetingSchedule
        fields = (
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
