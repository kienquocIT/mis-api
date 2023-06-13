from rest_framework import serializers

from apps.core.log.models import ActivityLog

__all__ = [
    'ActivityListSerializer',
]


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = (
            'id', 'request_method', 'date_created', 'doc_id', 'doc_app',
            'automated_logging', 'msg', 'data_change', 'change_partial',
            'user_data', 'employee_data', 'user_id', 'employee_id',
        )
