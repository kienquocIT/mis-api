__all__ = ['ProjectTaskListSerializers', 'ProjectTaskDetailSerializers', 'ProjectTaskListAllSerializers']

from rest_framework import serializers

from apps.shared import ProjectMsg
from ..extend_func import re_calc_work_group, calc_rate_project
from ..models import ProjectMapTasks
from ...task.models import OpportunityLogWork


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
    task = serializers.SerializerMethodField()

    @classmethod
    def get_task(cls, obj):
        task = obj.task
        emp_role = []
        if task.employee_inherit.role:
            emp_role = [
                {
                    'id': str(emp.id),
                    'title': emp.title
                } for emp in task.employee_inherit.role.all()
            ]
        list_log_time = OpportunityLogWork.objects.filter(
            task=task
        )
        task_log_work = []
        if list_log_time.count():
            task_log_work = [
                {
                    'id': item[0],
                    'start_date': item[1],
                    'end_date': item[2],
                    'time_spent': item[3],
                    'employee_created': {
                        'id': item[4],
                        'first_name': item[5],
                        'last_name': item[6],
                        'avatar': item[7]
                    },
                } for item in list_log_time.values_list(
                    'id', 'start_date', 'end_date', 'time_spent',
                    'employee_created_id',
                    'employee_created__first_name',
                    'employee_created__last_name',
                    'employee_created__avatar'
                )
            ]
        return {
            'id': str(task.id),
            'title': task.title,
            'code': task.code,
            'task_status': {
                'id': task.task_status.id,
                'title': task.task_status.title,
            } if task.task_status else {},
            'start_date': task.start_date,
            'end_date': task.end_date,
            'priority': task.priority,
            'employee_inherit': {
                'id': str(task.employee_inherit.id),
                'avatar': task.employee_inherit.avatar,
                'first_name': task.employee_inherit.first_name,
                'last_name': task.employee_inherit.last_name,
                'full_name': task.employee_inherit.get_full_name(),
                'role': emp_role,
            } if task.employee_inherit else {},
            'checklist': task.checklist if task.checklist else 0,
            'parent_n': {
                'id': task.parent_n.id,
                'title': task.parent_n.title,
                'code': task.parent_n.code
            } if task.parent_n else {},
            'employee_created': {
                'avatar': task.employee_created.avatar,
                'first_name': task.employee_created.first_name,
                'last_name': task.employee_created.last_name,
                'full_name': task.employee_created.get_full_name()
            } if task.employee_created else {},
            'date_created': task.date_created,
            'percent_completed': task.percent_completed,
            'estimate': task.estimate,
            'log_time': task_log_work,
            'project': task.project_data,
        } if task else {}

    class Meta:
        model = ProjectMapTasks
        fields = (
            'task',
        )
