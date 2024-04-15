__all__ = ['WorkListSerializers', 'WorkCreateSerializers', 'WorkDetailSerializers']

from rest_framework import serializers

from apps.shared import HRMsg, BaseMsg
from apps.shared.translations.sales import ProjectMsg
from ..models import ProjectWorks, Project, ProjectMapWork, GroupMapWork, ProjectGroups


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
            'group'
        )


class WorkDetailSerializers(serializers.ModelSerializer):
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

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
