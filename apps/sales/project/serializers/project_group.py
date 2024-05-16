__all__ = ['GroupCreateSerializers', 'GroupDetailSerializers', 'GroupListSerializers', 'GroupListDDSerializers']

from rest_framework import serializers

from ..models import Project, ProjectGroups, ProjectMapGroup
from apps.shared import HRMsg, BaseMsg
from apps.shared.translations.sales import ProjectMsg


class GroupCreateSerializers(serializers.ModelSerializer):
    project = serializers.UUIDField()

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

    def create(self, validated_data):
        project = validated_data.pop('project', None)
        group = ProjectGroups.objects.create(**validated_data)
        ProjectMapGroup.objects.create(project=project, group=group, tenant=group.tenant, company=group.company)
        return group

    class Meta:
        model = ProjectGroups
        fields = (
            'title',
            'employee_inherit',
            'gr_weight',
            'gr_rate',
            'gr_start_date',
            'gr_end_date',
            'project',
            'order',
        )


class GroupListSerializers(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return obj.employee_inherit_data
        return {}

    class Meta:
        model = ProjectGroups
        fields = (
            'id',
            'title',
            'employee_inherit',
            'gr_weight',
            'gr_rate',
            'gr_start_date',
            'gr_end_date',
            'order',
        )


class GroupDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProjectGroups
        fields = (
            'id',
            'title',
            'employee_inherit',
            'gr_weight',
            'gr_rate',
            'gr_start_date',
            'gr_end_date',
            'order',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class GroupListDDSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField()
    title = serializers.CharField()

    class Meta:
        model = ProjectMapGroup
        fields = (
            'id',
            'title',
        )
