__all__ = ['ProjectTaskListSerializers', 'ProjectTaskDetailSerializers', 'ProjectTaskListAllSerializers']

from rest_framework import serializers

from apps.shared import ProjectMsg
from ..extend_func import re_calc_work_group, calc_rate_project
from ..models import ProjectMapTasks
from ...task.models import OpportunityTask


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

    def validate(self, attrs):
        work = attrs['work'] if 'work' in attrs else None
        # nếu có work và loại qh là FS và work chưa finish
        if work and work.work_dependencies_parent and work.work_dependencies_type == 1 and \
                work.work_dependencies_parent.w_rate != 100:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_UPDATE_WORK_ERROR})
        return attrs

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
        calc_rate_project(instance.project)
        return instance


class ProjectTaskListAllSerializers(serializers.ModelSerializer):
    task_status = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_task_status(cls, obj):
        return {
            'id': obj.task_status.id,
            'title': obj.task_status.title
        } if obj.task_status else {}

    @classmethod
    def get_project(cls, obj):
        return {
            'id': obj.project.id,
            'title': obj.project.title,
            'code': obj.project.code
        } if obj.project else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            employee_data = obj.employee_inherit.get_detail_minimal()
            roles = obj.employee_inherit.role.all()
            employee_data["role"] = [{"id": role.id, "title": role.title} for role in roles] if roles else []
            return employee_data
        return {}

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_minimal() if obj.employee_created else {}

    class Meta:
        model = OpportunityTask
        fields = (
            'id',
            'title',
            'code',
            'task_status',
            'percent_completed',
            'priority',
            'employee_inherit',
            'employee_created',
            'start_date',
            'project',
            'log_time',
            'estimate'
        )
