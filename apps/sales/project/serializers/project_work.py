__all__ = ['WorkListSerializers', 'WorkCreateSerializers', 'WorkDetailSerializers']

from rest_framework import serializers

from apps.shared import HRMsg, BaseMsg
from apps.shared.translations.sales import ProjectMsg
from ..models import ProjectWorks, Project, ProjectMapWork, GroupMapWork, ProjectGroups


def validated_date_work(attrs):
    if 'work_dependencies_parent' in attrs:
        work_type = attrs['work_dependencies_type']
        if work_type == 1 and attrs['work_dependencies_parent'].w_end_date > attrs['w_start_date']:
            # nếu loại bắt đầu là "finish to start" và ngày kết thúc lớn hơn ngày bắt đầu của work tạo
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WORK_ERROR_DATE})
    if 'group' in attrs:
        if attrs['w_start_date'] < attrs['group'].gr_start_date or attrs['w_end_date'] > attrs['group'].gr_end_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WORK_ERROR_DATE})
    return attrs


class WorkListSerializers(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return obj.employee_inherit_data
        return {}

    class Meta:
        model = ProjectWorks
        fields = (
            'id',
            'title',
            'employee_inherit',
            'w_weight',
            'w_rate',
            'w_start_date',
            'w_end_date',
            'order',
        )


class WorkCreateSerializers(serializers.ModelSerializer):
    project = serializers.UUIDField()
    group = serializers.UUIDField(required=False)

    @classmethod
    def validate_employee_inherit(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_project(cls, value):
        try:
            pj = Project.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return pj
        except Project.DoesNotExist:
            raise serializers.ValidationError({'detail': f'{ProjectMsg.PROJECT} {BaseMsg.NOT_EXIST}'})

    @classmethod
    def validate_group(cls, value):
        try:
            pj_group = ProjectGroups.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return pj_group
        except Project.DoesNotExist:
            raise serializers.ValidationError({'detail': f'{ProjectMsg.PROJECT_GROUP} {BaseMsg.NOT_EXIST}'})

    def validate(self, attrs):
        return validated_date_work(attrs)

    def create(self, validated_data):
        project = validated_data.pop('project', None)
        group = validated_data.pop('group', None)
        work = ProjectWorks.objects.create(**validated_data)
        ProjectMapWork.objects.create(project=project, work=work)
        if group:
            GroupMapWork.objects.create(group=group, work=work)
        return work

    class Meta:
        model = ProjectWorks
        fields = (
            'title',
            'employee_inherit',
            'w_weight',
            'w_rate',
            'w_start_date',
            'w_end_date',
            'order',
            'project',
            'group',
            'work_dependencies_parent',
            'work_dependencies_type'
        )


class WorkDetailSerializers(serializers.ModelSerializer):
    work_dependencies_parent = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    @classmethod
    def get_work_dependencies_parent(cls, obj):
        if obj.work_dependencies_parent:
            return {
                "id": str(obj.work_dependencies_parent.id),
                "title": obj.work_dependencies_parent.title
            }
        return {}

    @classmethod
    def get_group(cls, obj):
        group_map_work = obj.project_groupmapwork_work.all().first()
        if group_map_work:
            return {
                "id": str(group_map_work.group.id),
                "title": group_map_work.group.title
            }
        return {}

    class Meta:
        model = ProjectWorks
        fields = (
            'id',
            'title',
            'employee_inherit',
            'w_weight',
            'w_rate',
            'w_start_date',
            'w_end_date',
            'order',
            'work_dependencies_parent',
            'work_dependencies_type',
            'group',
            'work_status',
        )

    def validate(self, attrs):
        return validated_date_work(attrs)

    def update(self, instance, validated_data):
        group = validated_data.pop('group', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if group:
            GroupMapWork.objects.filter(work=instance).delete()
            GroupMapWork.objects.create(group=group, work=instance)
        return instance
