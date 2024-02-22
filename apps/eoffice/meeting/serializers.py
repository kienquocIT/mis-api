from datetime import datetime, timedelta
from django.core.mail import get_connection, EmailMessage
import requests
from icalendar import Calendar, Event
from rest_framework import serializers
from apps.eoffice.meeting.models import (
    MeetingRoom, MeetingZoomConfig, MeetingSchedule, MeetingScheduleParticipant, MeetingScheduleOnlineMeeting,
    MeetingScheduleAttachmentFile
)
from apps.shared import MeetingScheduleMsg, SimpleEncryptor
from misapi import settings


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
        fields = ('id', 'personal_meeting_id')


class MeetingZoomConfigCreateSerializer(serializers.ModelSerializer):
    account_id = serializers.CharField(max_length=100)
    client_id = serializers.CharField(max_length=100)
    client_secret = serializers.CharField(max_length=100)

    class Meta:
        model = MeetingZoomConfig
        fields = (
            'account_email',
            'account_id',
            'client_id',
            'client_secret',
            'personal_meeting_id'
        )

    def validate(self, validate_data):
        password = SimpleEncryptor().generate_key(password=settings.EMAIL_CONFIG_PASSWORD)
        cryptor = SimpleEncryptor(key=password)
        validate_data['account_id'] = cryptor.encrypt(validate_data['account_id'])
        validate_data['client_id'] = cryptor.encrypt(validate_data['client_id'])
        validate_data['client_secret'] = cryptor.encrypt(validate_data['client_secret'])
        return validate_data

    def create(self, validated_data):
        MeetingZoomConfig.objects.filter_current(fill__tenant=True, fill__company=True).delete()
        zoom_config = MeetingZoomConfig.objects.create(**validated_data)
        return zoom_config


class MeetingZoomConfigDetailSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = MeetingZoomConfig
        fields = ()


# Meeting schedule

class MeetingScheduleSubFunction:
    @classmethod
    def create_participants_mapped(cls, meeting_schedule, participants_list):
        bulk_info = []
        for item in participants_list:
            bulk_info.append(
                MeetingScheduleParticipant(
                    meeting_schedule_mapped=meeting_schedule,
                    **item
                )
            )
        MeetingScheduleParticipant.objects.filter(meeting_schedule_mapped=meeting_schedule).delete()
        MeetingScheduleParticipant.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def create_online_meeting_object(cls, config_obj, zoom_meeting_obj):
        try:
            password = SimpleEncryptor().generate_key(password=settings.EMAIL_CONFIG_PASSWORD)
            cryptor = SimpleEncryptor(key=password)
            account_id = cryptor.decrypt(config_obj.account_id)
            client_id = cryptor.decrypt(config_obj.client_id)
            client_secret = cryptor.decrypt(config_obj.client_secret)
        except Exception as err:
            raise serializers.ValidationError({'Decrypting': f'Error while decrypting ({err})'})
        api_base_url = "https://api.zoom.us/v2"
        response = requests.post(
            "https://zoom.us/oauth/token",
            auth=(client_id, client_secret),
            data={
                "grant_type": "account_credentials",
                "account_id": account_id,
                "client_secret": client_secret
            },
            timeout=60
        )

        if response.status_code != 200:
            raise serializers.ValidationError({'Online meeting': 'Unable to get access token'})
        response_data = response.json()
        access_token = response_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        resp = requests.post(
            f"{api_base_url}/users/me/meetings",
            headers=headers,
            json=zoom_meeting_obj.meeting_create_payload,
            timeout=60
        )
        if resp.status_code != 201:
            raise serializers.ValidationError({'Online meeting': 'Unable to generate meeting link'})
        response_data = resp.json()

        zoom_meeting_obj.meeting_ID = response_data.get("pmi") if response_data.get("pmi") else response_data.get("id")
        zoom_meeting_obj.meeting_link = response_data.get("join_url")
        zoom_meeting_obj.meeting_passcode = response_data.get("password")
        zoom_meeting_obj.save(update_fields=["meeting_ID", "meeting_link", "meeting_passcode"])
        return response_data

    @classmethod
    def create_calendar_ics_file(cls, meeting_id, meeting_topic, meeting_host_email, start_date, start_time, duration):
        start_date = start_date.strftime('%Y-%m-%d').split('-')
        start_time = start_time.strftime('%H:%M').split(':')
        dt_start_data = datetime(
            int(start_date[0]), int(start_date[1]), int(start_date[2]), int(start_time[0]), int(start_time[1]), 0
        )
        dt_end_data = dt_start_data + timedelta(minutes=duration)
        calendar = Calendar()
        event = Event()
        event.add('summary', meeting_topic)
        event.add('organizer', meeting_host_email)
        event.add('dtstart', dt_start_data)
        event.add('dtend', dt_end_data)
        calendar.add_component(event)
        try:
            file_path = f'apps/eoffice/meeting/calendar_ics_file/calendar_{meeting_id}.ics'
            with open(file_path, 'wb') as file:
                file.write(calendar.to_ical())
            return file_path
        except Exception as error:
            raise serializers.ValidationError({'Online meeting': f'Cannot create calendar file ({error})'})

    @classmethod
    def send_mail(cls, meeting_schedule, response_data, meeting_time, date, time, duration):
        try:
            meeting_id = response_data.get('join_url').split('?')[0].split('/')[-1]
            email_to_list = []
            for item in meeting_schedule.meeting_schedule_mapped.all():
                if item.internal:
                    email_to_list.append(item.internal.email)
                if item.external:
                    email_to_list.append(item.external.email)

            email = EmailMessage(
                subject=response_data.get('topic'),
                body=f"{meeting_schedule.employee_inherit.get_full_name(2)} from {meeting_schedule.company.title} "
                     f"has invited you to a scheduled Zoom meeting."
                     f"\n\nTopic: {response_data.get('topic')}\nTime: {meeting_time}"
                     f"\n\nJoin Zoom Meeting\n{response_data.get('join_url')}"
                     f"\n\nMeeting ID: {meeting_id}"
                     f"\nPasscode: {response_data.get('password')}",
                from_email=meeting_schedule.company.email,
                to=email_to_list,
                cc=[],
                bcc=[],
                reply_to=[],
            )
            for attachment in [
                cls.create_calendar_ics_file(
                    meeting_id,
                    response_data.get('topic'),
                    meeting_schedule.employee_inherit.email,
                    date,
                    time,
                    duration
                )
            ]:
                email.attach_file(attachment)

            password = SimpleEncryptor().generate_key(password=settings.EMAIL_CONFIG_PASSWORD)
            connection = get_connection(
                username=meeting_schedule.company.email,
                password=SimpleEncryptor(key=password).decrypt(meeting_schedule.company.email_app_password),
                fail_silently=False,
            )
            email.connection = connection
            email.send()
            return True
        except Exception as err:
            company_obj = meeting_schedule.company
            if company_obj:
                company_obj.email_app_password_status = False
                company_obj.save(update_fields=['email_app_password_status'])
            raise serializers.ValidationError({
                'Online meeting': f"Cannot send email. {err.args[1]}. Try to renew your company's app password"
            })

    @classmethod
    def after_create_online_meeting(cls, meeting_schedule, online_meeting_data):
        MeetingScheduleOnlineMeeting.objects.filter(meeting_online_schedule_mapped=meeting_schedule).delete()
        zoom_meeting_obj = MeetingScheduleOnlineMeeting.objects.create(
            meeting_online_schedule_mapped=meeting_schedule,
            **online_meeting_data
        )
        meeting_config = MeetingZoomConfig.objects.filter_current(fill__tenant=True, fill__company=True)
        if meeting_config.exists():
            response_data = cls.create_online_meeting_object(meeting_config.first(), zoom_meeting_obj)
            duration = meeting_schedule.meeting_duration
            date = meeting_schedule.meeting_start_date
            time = meeting_schedule.meeting_start_time
            meeting_time = date.strftime('%Y-%m-%d') + ' ' + time.strftime('%H:%M') + ' ' + (
                'AM' if time.strftime('%H:%M').split(':')[0] < '12' else 'PM'
            )
            cls.send_mail(meeting_schedule, response_data, meeting_time, date, time, duration)
        return True

    @classmethod
    def check_room_overlap(cls, item, data):
        item_mt_time = f"{item.meeting_start_date} {item.meeting_start_time}"
        this_mt_time = f"{data.get('meeting_start_date')} {data.get('meeting_start_time')}"
        item_mt_datetime = datetime.strptime(item_mt_time, "%Y-%m-%d %H:%M:%S")
        this_mt_datetime = datetime.strptime(this_mt_time, "%Y-%m-%d %H:%M:%S")
        item_end_datetime = item_mt_datetime + timedelta(minutes=item.meeting_duration)
        this_end_datetime = this_mt_datetime + timedelta(minutes=data.get('meeting_duration'))
        return (item_mt_datetime < this_end_datetime) and (this_mt_datetime < item_end_datetime)

    @classmethod
    def create_files_mapped(cls, meeting_obj, file_id_list):
        try:
            bulk_data_file = []
            for index, file_id in enumerate(file_id_list):
                bulk_data_file.append(MeetingScheduleAttachmentFile(
                    meeting_schedule=meeting_obj,
                    attachment_id=file_id,
                    order=index
                ))
            MeetingScheduleAttachmentFile.objects.filter(meeting_schedule=meeting_obj).delete()
            MeetingScheduleAttachmentFile.objects.bulk_create(bulk_data_file)
            return True
        except Exception as err:
            raise serializers.ValidationError({'files': MeetingScheduleMsg.SAVE_FILES_ERROR + f' {err}'})


class MeetingScheduleListSerializer(serializers.ModelSerializer):  # noqa
    date_occur = serializers.SerializerMethodField()

    class Meta:
        model = MeetingSchedule
        fields = (
            'id',
            'title',
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


class MeetingScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'

    def validate(self, validate_data):
        # if validate_data.get('meeting_type') is True:
        #     # check room
        #     all_offline_meeting = MeetingSchedule.objects.filter_current(
        #         fill__company=True,
        #         fill__tenant=True,
        #         meeting_type=True,
        #         meeting_room_mapped=validate_data.get('meeting_room_mapped')
        #     )
        #     for item in all_offline_meeting:
        #         if check_room_overlap(item, validate_data):
        #             raise serializers.ValidationError({'room': MeetingScheduleMsg.ROOM_IS_NOT_AVAILABLE})
        return validate_data

    def create(self, validated_data):
        meeting_schedule = MeetingSchedule.objects.create(
            **validated_data, employee_inherit_id=validated_data['employee_created_id']
        )
        MeetingScheduleSubFunction.create_participants_mapped(
            meeting_schedule, self.initial_data.get('participants', [])
        )
        if meeting_schedule.meeting_type is False:
            MeetingScheduleSubFunction.after_create_online_meeting(
                meeting_schedule, self.initial_data.get('online_meeting_data', {})
            )

        attachment = self.initial_data.get('attachment', '')
        if attachment:
            MeetingScheduleSubFunction.create_files_mapped(meeting_schedule, attachment.strip().split(','))
        return meeting_schedule


class MeetingScheduleDetailSerializer(serializers.ModelSerializer):  # noqa
    participants = serializers.SerializerMethodField()
    meeting_room_mapped = serializers.SerializerMethodField()
    online_meeting_data = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

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
            'online_meeting_data',
            'attachment'
        )

    @classmethod
    def get_participants(cls, obj):
        participants = [{
            'internal': {
                'id': item.internal_id,
                'full_name': item.internal.get_full_name(2)
            } if item.internal else None,
            'external': {
                'id': item.external_id,
                'full_name': item.external.fullname
            } if item.external else None,
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

    @classmethod
    def get_attachment(cls, obj):
        att_objs = MeetingScheduleAttachmentFile.objects.select_related('attachment').filter(meeting_schedule=obj)
        return [item.attachment.get_detail() for item in att_objs]


class MeetingScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'
