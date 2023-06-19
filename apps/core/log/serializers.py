from rest_framework import serializers

from apps.core.log.models import (
    ActivityLog,
    Notifications,
)

__all__ = [
    'ActivityListSerializer',
    'NotifyListSerializer',
    'NotifyUpdateDoneSerializer',
]

from apps.shared import WorkflowMsgNotify


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = (
            'id', 'request_method', 'date_created', 'doc_id', 'doc_app',
            'automated_logging', 'msg', 'data_change', 'change_partial',
            'user_data', 'employee_data', 'user_id', 'employee_id',
        )


class NotifyListSerializer(serializers.ModelSerializer):
    msg = serializers.SerializerMethodField()

    @classmethod
    def get_msg(cls, obj):
        return WorkflowMsgNotify.translate_msg(obj.msg)

    class Meta:
        model = Notifications
        fields = (
            'id',
            'date_created',
            'title',
            'msg',
            'doc_id',
            'doc_app',
            'automated_sending',
            'is_done',
            'user_id',
            'user_data',
            'employee_id',
            'employee_data',
            'employee_sender_id',
            'employee_sender_data',
        )


class NotifyUpdateDoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ('is_done',)
