from rest_framework import serializers

from apps.sales.task.models.config import TaskConfig


__all__ = [
    'TaskConfigDetailSerializer',
    'TaskConfigUpdateSerializer',
]


class TaskConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfig
        fields = ('id', 'list_status', )


class TaskConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfig
        fields = ('list_status', )
