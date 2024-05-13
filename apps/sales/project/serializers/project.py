__all__ = ['ProjectListSerializers', 'ProjectCreateSerializers', 'ProjectDetailSerializers', 'ProjectUpdateSerializers',
           'ProjectUpdateOrderSerializers'
           ]

from rest_framework import serializers

from apps.core.hr.models import Employee
from ..extend_func import pj_get_alias_permit_from_app
from ..models import Project, ProjectMapMember, ProjectWorks, ProjectGroups
from apps.shared import HRMsg, FORMATTING, ProjectMsg


class ProjectListSerializers(serializers.ModelSerializer):
    works = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    project_owner = serializers.SerializerMethodField()

    @classmethod
    def get_works(cls, obj):
        work = {"all": 0, "completed": 0}
        works = obj.project_projectmapwork_project.all()
        if works:
            for item in works:
                if item.work.w_rate == 100:
                    work['completed'] += 1
            work['all'] = works.count()
        return work

    @classmethod
    def get_tasks(cls, obj):
        task = {"all": 0, "completed": 0}
        tasks = obj.project_projectmaptasks_project.all()
        if tasks:
            for item in tasks:
                if item.task.percent_completed == 100:
                    task['completed'] += 1
            task['all'] = tasks.count()
        return task

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return obj.employee_inherit_data
        return {}

    @classmethod
    def get_project_owner(cls, obj):
        if obj.project_owner:
            return obj.project_owner_data
        return {}

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'code',
            'project_owner',
            'employee_inherit',
            'start_date',
            'finish_date',
            'completion_rate',
            'works',
            'tasks',
            'system_status',
        )


class ProjectCreateSerializers(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return str(value)

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)

        # create project team member
        permission_by_configured = pj_get_alias_permit_from_app(employee_obj=project.employee_inherit)
        ProjectMapMember.objects.create(
            tenant_id=project.tenant_id,
            company_id=project.company_id,
            project=project,
            member=project.employee_inherit,
            permit_add_member=True,
            permit_add_gaw=True,
            permit_view_this_project=True,
            permission_by_configured=permission_by_configured
        )
        return project

    class Meta:
        model = Project
        fields = (
            'title',
            'employee_inherit_id',
            'project_owner',
            'start_date',
            'finish_date',
            'system_status'
        )


class ProjectDetailSerializers(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    works = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    project_owner = serializers.SerializerMethodField()

    @classmethod
    def get_groups(cls, obj):
        if obj:
            groups_list = obj.project_projectmapgroup_project.all()
            groups = []
            for item in groups_list:
                groups.append(
                    {
                        "id": str(item.group.id),
                        "title": item.group.title,
                        "date_from": FORMATTING.parse_datetime(item.group.gr_start_date),
                        "date_end": FORMATTING.parse_datetime(item.group.gr_end_date),
                        "order": item.group.order,
                        "progress": item.group.gr_rate,
                        "weight": item.group.gr_weight
                    }
                )
            return groups
        return []

    @classmethod
    def get_works(cls, obj):
        if obj:
            pj_works = obj.project_projectmapwork_project.all()
            works_list = []
            for item in pj_works:
                temp = {
                    "id": str(item.work.id),
                    "title": item.work.title,
                    "work_status": item.work.work_status,
                    "date_from": item.work.w_start_date,
                    "date_end": item.work.w_end_date,
                    "order": item.work.order,
                    "group": "",
                    "relationships_type": None,
                    "dependencies_parent": "",
                    "progress": item.work.w_rate,
                    "weight": item.work.w_weight,
                }
                group_mw = item.work.project_groupmapwork_work.all()
                if group_mw:
                    group_mw = group_mw.first()
                    temp['group'] = str(group_mw.group.id)
                if item.work.work_dependencies_type is not None:
                    temp['relationships_type'] = item.work.work_dependencies_type
                if item.work.work_dependencies_parent:
                    temp['dependencies_parent'] = str(item.work.work_dependencies_parent.id)
                works_list.append(temp)
            return works_list
        return []

    def get_members(self, obj):
        allow_get_member = self.context.get('allow_get_member', False)
        return [
            {
                "id": item.id,
                "first_name": item.first_name,
                "last_name": item.last_name,
                "full_name": item.get_full_name(),
                "email": item.email,
                "avatar": item.avatar,
                "is_active": item.is_active,
            } for item in obj.members.all()
        ] if allow_get_member else []

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return obj.employee_inherit_data
        return {}

    @classmethod
    def get_project_owner(cls, obj):
        if obj.project_owner:
            return obj.project_owner_data
        return {}

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'code',
            'start_date',
            'finish_date',
            'completion_rate',
            'project_owner',
            'employee_inherit',
            'system_status',
            'works',
            'groups',
            'members',
        )


class ProjectUpdateSerializers(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField(required=False)
    project_owner = serializers.UUIDField(required=False)

    @classmethod
    def validate_project_owner(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})

    class Meta:
        model = Project
        fields = (
            'title',
            'start_date',
            'finish_date',
            'project_owner',
            'employee_inherit_id',
            'system_status'
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ProjectUpdateOrderSerializers(serializers.ModelSerializer):
    list_update = serializers.JSONField()

    class Meta:
        model = Project
        fields = (
            'list_update',
        )

    @classmethod
    def work_update_order(cls, work_lst):
        try:
            lst_update = []
            for work in work_lst:
                crt_w = ProjectWorks.objects.get(id=work['id'])
                crt_w.order = work['order']
                lst_update.append(crt_w)
            ProjectWorks.objects.bulk_update(lst_update, fields=['order'])
        except ProjectWorks.DoesNotExist:
            raise serializers.ValidationError({'detail': ProjectMsg.WORK_NOT_EXIST})

    @classmethod
    def group_update_order(cls, group_lst):
        try:
            lst_update = []
            for group in group_lst:
                crt_g = ProjectGroups.objects.get(id=group['id'])
                crt_g.order = group['order']
                lst_update.append(crt_g)
            ProjectGroups.objects.bulk_update(lst_update, fields=['order'])
        except ProjectGroups.DoesNotExist:
            raise serializers.ValidationError({'detail': ProjectMsg.GROUP_NOT_EXIST})

    def update(self, instance, validated_data):
        list_update = validated_data.pop('list_update')
        work_list = list_update.get('work', [])
        group_list = list_update.get('group', [])
        if work_list:
            self.work_update_order(work_list)
        if group_list:
            self.group_update_order(group_list)
        return instance
