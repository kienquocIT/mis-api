__all__ = ['WorkListSerializers', 'WorkCreateSerializers', 'WorkDetailSerializers', 'WorkUpdateSerializers']

from rest_framework import serializers

from apps.shared import HRMsg, BaseMsg, ProjectMsg
from ..extend_func import reorder_work, calc_rate_project, group_calc_weight, work_calc_weight_h_group
from ..models import ProjectWorks, Project, ProjectMapWork, GroupMapWork, ProjectGroups


def validated_date_work(attrs, w_rate=None):
    if 'work_dependencies_parent' in attrs and hasattr(attrs['work_dependencies_parent'], 'id'):
        work_type = attrs['work_dependencies_type'] if 'work_dependencies_type' in attrs else 0
        work_parent = attrs['work_dependencies_parent']

        # nếu loại bắt đầu là "finish to start" và ngày kết thúc lớn hơn ngày bắt đầu của work tạo
        if work_type == 1 and work_parent.w_end_date >= attrs['w_start_date'] \
                or attrs['w_start_date'] < work_parent.w_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WORK_ERROR_DATE})

        # nếu công việc tự phụ thuộc chính nó thì báo lỗi
        parent_id = getattr(work_parent, 'id', None)
        if parent_id and parent_id == attrs.get('id'):
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DEPENDENCIES_ERROR})

        # nếu loại "FS" và work dc phụ thuộc chưa finish, và work rate > 0
        if work_type == 1 and (w_rate and w_rate > 0) and work_parent.w_rate != 100:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_UPDATE_WORK_ERROR})
    if 'group' in attrs:
        group_obj = attrs['group']
        if group_obj:
            if attrs['w_start_date'] < group_obj.gr_start_date or attrs['w_end_date'] > group_obj.gr_end_date:
                raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WORK_ERROR_DATE2})
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
            prj = Project.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return prj
        except Project.DoesNotExist:
            raise serializers.ValidationError({'detail': f'{ProjectMsg.PROJECT} {BaseMsg.NOT_EXIST}'})

    @classmethod
    def validate_group(cls, value):
        try:
            group = ProjectGroups.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return group
        except ProjectGroups.DoesNotExist:
            return value

    def validate(self, attrs):
        attrs['employee_inherit'] = attrs['project'].employee_inherit
        w_start_date = attrs['w_start_date']
        w_end_date = attrs['w_end_date']
        if w_end_date < w_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})

        project = attrs['project']
        group = attrs['group'] if 'group' in attrs else None
        if group:
            value = work_calc_weight_h_group(attrs['w_weight'], group)
            if not bool(value):
                raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
            attrs['w_weight'] = value
        else:
            attrs['w_weight'] = group_calc_weight(project, attrs['w_weight'])
        return validated_date_work(attrs)

    def create(self, validated_data):
        project = validated_data.pop('project', None)
        group = validated_data.pop('group', None)
        if group and project:
            validated_data['order'] = reorder_work(group, project)

        work = ProjectWorks.objects.create(**validated_data)
        ProjectMapWork.objects.create(
            project=project, work=work,
            tenant=work.tenant,
            company=work.company,
        )
        if group:
            GroupMapWork.objects.create(group=group, work=work)
        calc_rate_project(project)
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


class WorkUpdateSerializers(serializers.ModelSerializer):
    group = serializers.UUIDField(required=False)

    class Meta:
        model = ProjectWorks
        fields = (
            'title',
            'w_weight',
            'w_start_date',
            'w_end_date',
            'work_dependencies_parent',
            'work_dependencies_type',
            'group',
        )

    @classmethod
    def validate_group(cls, value):
        try:
            group = ProjectGroups.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
            return group
        except ProjectGroups.DoesNotExist:
            return value

    def validate(self, attrs):
        w_rate = self.instance.w_rate
        w_start_date = attrs['w_start_date']
        w_end_date = attrs['w_end_date']
        if w_end_date < w_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})
        # valid group
        project_map = self.instance.project_projectmapwork_work.all().first()
        group = attrs['group'] if 'group' in attrs else None
        if group:
            value = work_calc_weight_h_group(attrs['w_weight'], group, self.instance)
            if not bool(value):
                raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
            attrs['w_weight'] = value
        else:
            attrs['w_weight'] = group_calc_weight(project_map.project, attrs['w_weight'])
        return validated_date_work(attrs, w_rate)

    def update(self, instance, validated_data):
        group = validated_data.pop('group', None)
        prj_id = self.context.get('project', None)
        prj_obj = Project.objects.get(id=prj_id)
        if group and prj_obj:
            validated_data['order'] = reorder_work(group, prj_obj)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # create or update group
        if group:
            GroupMapWork.objects.get_or_create(group=group, work=instance)
        else:
            old_g_obj = GroupMapWork.objects.get(work=instance)
            old_g_obj.delete()
        # re calc rate of project after update work
        calc_rate_project(prj_obj)
        return instance
