from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.eoffice.meeting.models import MeetingRoom, MeetingZoomConfig, MeetingSchedule


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
        fields = '__all__'

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


class MeetingScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'


class MeetingScheduleDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = MeetingSchedule
        fields = '__all__'


class MeetingScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSchedule
        fields = '__all__'
