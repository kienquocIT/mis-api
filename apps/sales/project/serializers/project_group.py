__all__ = ['GroupCreateSerializers', 'GroupDetailSerializers', 'GroupListSerializers', 'GroupListDDSerializers']

from rest_framework import serializers

from apps.shared import HRMsg, BaseMsg, ProjectMsg
from ..extend_func import calc_rate_project, group_calc_weight, group_update_weight
from ..models import Project, ProjectGroups, ProjectMapGroup


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
            prj = Project.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return prj
        except Project.DoesNotExist:
            raise serializers.ValidationError({'detail': f'{ProjectMsg.PROJECT} {BaseMsg.NOT_EXIST}'})

    def validate(self, attrs):
        gr_end_date = attrs['gr_end_date']
        gr_start_date = attrs['gr_start_date']
        if gr_end_date < gr_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})
        # valid weight
        project = attrs['project']
        value = group_calc_weight(project, attrs['gr_weight'])
        if attrs['gr_weight'] == 0:
            attrs['gr_weight'] = value
        if bool(value) is False:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
        return attrs

    def create(self, validated_data):
        project = validated_data.pop('project', None)
        group = ProjectGroups.objects.create(**validated_data)
        ProjectMapGroup.objects.create(project=project, group=group, tenant=group.tenant, company=group.company)
        calc_rate_project(project)
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

    def validate(self, attrs):
        gr_end_date = attrs['gr_end_date']
        gr_start_date = attrs['gr_start_date']
        project = self.instance.project_projectmapgroup_group.all().first().project
        if gr_end_date < gr_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})

        if gr_start_date < project.start_date or gr_start_date > project.finish_date or \
                gr_end_date > project.finish_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_VALID_ERROR})
        # valid weight
        value = group_update_weight(project, attrs['gr_weight'], self.instance)
        if bool(value) is False:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
        return attrs

    def update(self, instance, validated_data):
        weight_before = instance.gr_weight
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if validated_data['gr_weight'] != weight_before:
            calc_rate_project(instance.project_projectmapgroup_group.all().first().project)
        return instance


class GroupListDDSerializers(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    @classmethod
    def get_group(cls, obj):
        if obj.group:
            return {
                'id': str(obj.group.id),
                'title': obj.group.title,
            }
        return {}

    class Meta:
        model = ProjectMapGroup
        fields = (
            'id',
            'title',
            'group',
        )
