__all__ = ['ProjectListSerializers', 'ProjectCreateSerializers', 'ProjectDetailSerializers', 'ProjectUpdateSerializers',
           ]

from rest_framework import serializers

from apps.core.hr.models import Employee
from ..extend_func import pj_get_alias_permit_from_app
from ..models import Project, ProjectMapMember
from apps.shared import HRMsg, FORMATTING


class ProjectListSerializers(serializers.ModelSerializer):
    works = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    project_owner = serializers.SerializerMethodField()

    @classmethod
    def get_works(cls, obj):
        return {}

    @classmethod
    def get_tasks(cls, obj):
        return {}

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
                        "progress": item.group.gr_rate
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
