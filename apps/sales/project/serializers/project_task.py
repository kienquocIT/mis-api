__all__ = ['ProjectTaskListSerializers', 'ProjectTaskCreateSerializers', 'ProjectTaskDetailSerializers']

from rest_framework import serializers

from apps.shared import DisperseModel, ProjectMsg
from ..models import ProjectMapTasks
from ...task.serializers import OpportunityTaskCreateSerializer


def valid_user_create_update_delete(permit, user_crt, task_info):
    has_checked = False
    if permit:
        has_checked = True
    else:
        # ko có quyền thì check tiếp
        if hasattr(task_info, 'id'):
            # nếu là update task employee_inherit là user request
            task_info.employee_inherit = user_crt
            has_checked = True
        elif hasattr(task_info, 'parent_n') and not hasattr(task_info, 'id'):
            # nếu là create thì chỉ dc tạo sub-task
            has_checked = True
    return has_checked


class ProjectTaskListSerializers(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()

    @classmethod
    def get_task(cls, obj):
        return {
            'id': str(obj.task.id),
            'title': obj.task.title
        }

    class Meta:
        model = ProjectMapTasks
        fields = (
            'id',
            'task',
            'work'
        )


class ProjectTaskCreateSerializers(serializers.ModelSerializer):
    task = serializers.JSONField()

    class Meta:
        model = ProjectMapTasks
        fields = (
            'task',
            'work',
            'member',
            'project',
        )

    @classmethod
    def validate_project(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError({'members': ProjectMsg.PROJECT_REQUIRED})

    def valid_and_create_task(self, task_data):
        employee_crt = self.context.get('employee_current', None)
        permit_add = self.context.get('has_permit_add', None)
        task_data = OpportunityTaskCreateSerializer(data=task_data)
        task_data.is_valid(raise_exception=True)
        is_check = valid_user_create_update_delete(permit_add, employee_crt, task_data)
        if is_check:
            return task_data.save()
        raise serializers.ValidationError({'Employee': ProjectMsg.PERMISSION_ERROR})

    def create(self, validated_data):
        task = self.valid_and_create_task(validated_data.pop('task'))
        objs = ProjectMapTasks.objects.create(
            project=validated_data.get('project'),
            member_id=validated_data.get('member'),
            tenant_id=validated_data.get('tenant_id'),
            company_id=validated_data.get('company_id'),
            task=task
        )
        return objs


class ProjectTaskDetailSerializers(serializers.ModelSerializer):
    work = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    @classmethod
    def get_work(cls, obj):
        if obj.work:
            return {
                "id": str(obj.work.id),
                "title": obj.work.title
            }
        return {}

    @classmethod
    def get_member(cls, obj):
        if obj.member:
            return {
                "id": str(obj.member.id),
                "full_name": obj.member.get_full_name(),
                "first_name": obj.member.first_name,
                "last_name": obj.member.last_name
            }
        return {}

    @classmethod
    def get_task(cls, obj):
        if obj.task:
            return {
                "id": str(obj.task.id),
                "title": obj.task.title
            }
        return {}

    @classmethod
    def get_project(cls, obj):
        if obj.project:
            return {
                "id": str(obj.project.id),
                "title": obj.project.title
            }
        return {}

    class Meta:
        model = ProjectMapTasks
        fields = (
            'id',
            'task',
            'work',
            'member',
            'project',
        )
