from rest_framework import serializers

from apps.sales.task.models.config import OpportunityTaskConfig


__all__ = [
    'TaskConfigDetailSerializer',
    'TaskConfigUpdateSerializer',
]


class TaskConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTaskConfig
        fields = ('id', 'list_status')


class TaskConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTaskConfig
        fields = ('list_status', )
