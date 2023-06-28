from django.db.models import Max
from rest_framework import serializers

from apps.core.log.models import (
    ActivityLog,
    Notifications, BookMark, DocPined,
)

__all__ = [
    'ActivityListSerializer',
    'NotifyListSerializer',
    'NotifyUpdateDoneSerializer',
    'BookMarkListSerializer',
    'BookMarkCreateSerializer',
    'BookMarkUpdateSerializer',
    'DocPinedListSerializer',
    'DocPinedCreateSerializer',
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


class BookMarkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookMark
        fields = ('id', 'title', 'kind', 'view_name', 'customize_url', 'box_style', 'order', 'date_created')


class BookMarkCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        max_order = BookMark.objects.filter(
            employee_id=validated_data['employee_id']
        ).aggregate(max_value=Max('order'))['max_value']
        validated_data['order'] = max_order + 1 if isinstance(max_order, int) else 1
        instance = BookMark.objects.create(**validated_data)
        return instance

    class Meta:
        model = BookMark
        fields = ('title', 'kind', 'view_name', 'customize_url', 'box_style')


class BookMarkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookMark
        fields = ('title', 'kind', 'view_name', 'customize_url', 'box_style', 'order')


class DocPinedListSerializer(serializers.ModelSerializer):
    runtime = serializers.SerializerMethodField()

    @classmethod
    def get_runtime(cls, obj):
        if obj.runtime:
            stage_current_obj = obj.runtime.stage_currents
            assignees = [
                {
                    'employee_id': x.employee_id,
                    'employee_data': x.employee_data,
                    'action_perform': x.action_perform,
                    'is_done': x.is_done,
                    'date_created': x.date_created,
                } for x in stage_current_obj.assignee_of_runtime_stage.all()
            ] if stage_current_obj else []
            return {
                'id': str(obj.runtime_id),
                'doc_id': str(obj.runtime.doc_id),
                'doc_title': str(obj.runtime.doc_title),
                'app_code': str(obj.runtime.app_code),
                'app_id': str(obj.runtime.app_id),
                'stage_currents': {
                    'id': str(stage_current_obj.id),
                    'title': str(stage_current_obj.title),
                    'code': str(stage_current_obj.code),
                } if stage_current_obj else {},
                'assignees': assignees
            }
        return {}

    class Meta:
        model = DocPined
        fields = ('id', 'date_created', 'title', 'runtime')


class DocPinedCreateSerializer(serializers.ModelSerializer):
    runtime_id = serializers.UUIDField(required=True)

    class Meta:
        model = DocPined
        fields = ('runtime_id',)
