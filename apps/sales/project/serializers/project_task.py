__all__ = ['ProjectTaskListSerializers', 'ProjectTaskDetailSerializers']

from rest_framework import serializers

from ..extend_func import re_calc_work_group
from ..models import ProjectMapTasks


class ProjectTaskListSerializers(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()

    @classmethod
    def get_task(cls, obj):
        return {
            'id': str(obj.task.id),
            'title': obj.task.title,
            'code': obj.task.code
        } if obj.task else {}

    @classmethod
    def get_percent(cls, obj):
        if obj.task:
            return obj.task.percent_completed if obj.task.percent_completed > 0 else 0
        return 0

    @classmethod
    def get_assignee(cls, obj):
        if hasattr(obj, 'task'):
            task = obj.task
            assignee = {
                "id": str(obj.task.employee_inherit_id),
                "full_name": obj.task.employee_inherit.get_full_name(),
                "first_name": obj.task.employee_inherit.first_name,
                "last_name": obj.task.employee_inherit.last_name
            } if task and hasattr(task, 'employee_inherit') else {}
            return assignee
        return {}

    class Meta:
        model = ProjectMapTasks
        fields = (
            'id',
            'task',
            'work',
            'percent',
            'assignee',
            'work_before'
        )


class ProjectTaskDetailSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProjectMapTasks
        fields = (
            'work',
        )

    def update(self, instance, validated_data):
        unlink = self.context.get('unlink_work', None)
        work = validated_data.get('work') if unlink is None else instance.work
        if instance.work is not None or unlink:
            setattr(instance, 'work_before', {"id": str(instance.work.id), 'title': instance.work.title})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if unlink:
            instance.work = None
        instance.save()
        # re caculator percent rate after link or unlink task in work and group
        re_calc_work_group(work)
        return instance
