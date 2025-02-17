__all__ = ['GroupCreateSerializers', 'GroupDetailSerializers', 'GroupListSerializers', 'GroupListDDSerializers']

from rest_framework import serializers

from apps.shared import HRMsg, BaseMsg, ProjectMsg
from ..extend_func import calc_rate_project, group_calc_weight, group_update_weight, sort_order_work_and_group
from ..models import Project, ProjectGroups, ProjectMapGroup


def update_prj_finish_date(prj, validated_data):
    is_lock = prj.finish_date_lock
    if is_lock is False and validated_data['gr_end_date'] > prj.finish_date:
        prj.finish_date = validated_data['gr_end_date']
        prj.save(update_fields=['finish_date'])


class GroupCreateSerializers(serializers.ModelSerializer):
    project = serializers.UUIDField()
    sort_style = serializers.BooleanField(required=False, allow_null=True)

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
        project = attrs['project']

        if gr_end_date < gr_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})

        if gr_start_date < project.start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_VALID_ERROR})

        if project.finish_date_lock is True and gr_end_date > project.finish_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_INVALID_GROUP_DATE})

        # valid weight
        value = group_calc_weight(project, 0, attrs['gr_weight'])
        if attrs['gr_weight'] == 0:
            attrs['gr_weight'] = value
        if value is False:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
        return attrs

    def create(self, validated_data):
        project = validated_data.pop('project', None)
        is_sort = validated_data.pop('sort_style', None)
        group = ProjectGroups.objects.create(**validated_data)
        ProjectMapGroup.objects.create(project=project, group=group, tenant=group.tenant, company=group.company)
        calc_rate_project(project)
        update_prj_finish_date(project, validated_data)
        if is_sort is True:
            sort_order_work_and_group(group, project)
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
            'sort_style',
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

        if gr_start_date < project.start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_VALID_ERROR})

        if project.finish_date_lock is True and gr_end_date > project.finish_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_INVALID_GROUP_DATE})

        # valid weight
        value = group_update_weight(project, self.instance.gr_weight, attrs['gr_weight'])
        if attrs['gr_weight'] == 0:
            attrs['gr_weight'] = value
        if value is False:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
        return attrs

    def update(self, instance, validated_data):
        weight_before = instance.gr_weight
        prj = instance.project_projectmapgroup_group.all().first().project
        update_prj_finish_date(prj, validated_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if validated_data['gr_weight'] != weight_before:
            calc_rate_project(prj)
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
