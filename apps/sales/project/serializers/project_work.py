__all__ = ['WorkListSerializers', 'WorkCreateSerializers', 'WorkDetailSerializers', 'WorkUpdateSerializers']

from rest_framework import serializers

from apps.shared import HRMsg, BaseMsg, ProjectMsg, DisperseModel, call_task_background

from ..extend_func import reorder_work, calc_rate_project, group_calc_weight, work_calc_weight_h_group
from ..models import ProjectWorks, Project, ProjectMapWork, GroupMapWork, ProjectGroups, WorkMapBOM
from ..tasks import create_project_news


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
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_UPDATE_WORK_ERROR2})
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
    bom_service = serializers.UUIDField(required=False)

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

    @classmethod
    def validate_bom_service(cls, value):
        try:
            bom = DisperseModel(app_model='production.BOM').get_model().objects.get(
                id=value,
            )
            return bom
        except ValueError:
            return value

    def validate(self, attrs):
        attrs['employee_inherit'] = attrs['project'].employee_inherit
        w_start_date = attrs['w_start_date']
        w_end_date = attrs['w_end_date']
        project = attrs['project']

        if w_end_date < w_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})

        if w_start_date < project.start_date or w_start_date > project.finish_date or \
                w_end_date > project.finish_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_VALID_ERROR})

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
        bom_service = validated_data.pop('bom_service', None)
        if group and project:
            validated_data['order'] = reorder_work(group, project)
        if bom_service:
            validated_data['bom_data'] = {
                'id': str(bom_service.id),
                'title': bom_service.title,
                'code': bom_service.code
            }
        work = ProjectWorks.objects.create(**validated_data)
        ProjectMapWork.objects.create(
            project=project, work=work,
            tenant=work.tenant,
            company=work.company,
        )
        if group:
            GroupMapWork.objects.create(group=group, work=work)
        calc_rate_project(project)

        if bom_service:
            WorkMapBOM.objects.create(bom=bom_service, work=work)

        # create news feed
        call_task_background(
            my_task=create_project_news,
            **{
                'project_id': str(project.id),
                'employee_inherit_id': str(work.employee_inherit.id),
                'employee_created_id': str(work.employee_created.id),
                'application_id': str('49fe2eb9-39cd-44af-b74a-f690d7b61b67'),
                'document_id': str(work.id),
                'document_title': str(work.title),
                'title': ProjectMsg.CREATED_A,
                'msg': '',
            }
        )
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
            'work_dependencies_type',
            'bom_service'
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
            'bom_data'
        )


class WorkUpdateSerializers(serializers.ModelSerializer):
    group = serializers.UUIDField(required=False)
    bom_service = serializers.UUIDField(required=False)

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
            'bom_service',
        )

    @classmethod
    def re_calc_rate(cls, group):
        work_map = group.project_groupmapwork_group.all()
        if work_map:
            group.gr_rate = 0
            g_rate_temp = 0
            for item in work_map:
                item_w = item.work
                if item_w.w_weight and item_w.w_rate:
                    g_rate_temp += (item_w.w_rate / 100) * item_w.w_weight
            group.gr_rate = round(g_rate_temp, 1)
            group.save()

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

    @classmethod
    def validate_bom_service(cls, value):
        try:
            bom = DisperseModel(app_model='production.BOM').get_model().objects.get(
                id=value,
            )
            return bom
        except ValueError:
            return value

    def validate(self, attrs):
        w_rate = self.instance.w_rate
        w_start_date = attrs['w_start_date']
        w_end_date = attrs['w_end_date']
        if w_end_date < w_start_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_ERROR})
        # valid group
        project = self.instance.project_projectmapwork_work.all().first().project
        group = attrs['group'] if 'group' in attrs else None
        if group:
            value = work_calc_weight_h_group(attrs['w_weight'], group, self.instance)
            if not bool(value):
                raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_WEIGHT_ERROR})
            attrs['w_weight'] = value
        else:
            attrs['w_weight'] = group_calc_weight(project, attrs['w_weight'])

        if w_start_date < project.start_date or w_start_date > project.finish_date or \
                w_end_date > project.finish_date:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_DATE_VALID_ERROR})
        return validated_date_work(attrs, w_rate)

    def update(self, instance, validated_data):
        group = validated_data.pop('group', None)
        prj_id = self.context.get('project', None)
        bom_service = validated_data.pop('bom_service', None)
        if bom_service:
            validated_data['bom_data'] = {
                'id': str(bom_service.id),
                'title': bom_service.title,
                'code': bom_service.code
            }
        else:
            WorkMapBOM.objects.filter(work=instance).delete()
            validated_data['bom_data'] = {}
        prj_obj = Project.objects.get(id=prj_id)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        # create or update group
        if group:
            GroupMapWork.objects.get_or_create(group=group, work=instance)
            self.re_calc_rate(group)
        else:
            old_g_obj = GroupMapWork.objects.filter(work=instance)
            if old_g_obj.exists():
                old_g_obj.delete()
        # re SUM all rate group, work in project
        calc_rate_project(prj_obj)

        # create news feed
        call_task_background(
            my_task=create_project_news,
            **{
                'project_id': str(prj_obj.id),
                'employee_inherit_id': str(instance.employee_inherit.id),
                'employee_created_id': str(instance.employee_created.id),
                'application_id': str('49fe2eb9-39cd-44af-b74a-f690d7b61b67'),
                'document_id': str(instance.id),
                'document_title': str(instance.title),
                'title': ProjectMsg.UPDATED_A,
                'msg': '',
            }
        )
        return instance
