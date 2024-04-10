__all__ = ['ProjectListSerializers', 'ProjectCreateSerializers', 'ProjectDetailSerializers', 'ProjectUpdateSerializers',
           'GroupCreateSerializers', 'GroupDetailSerializers', 'GroupListSerializers', 'WorkListSerializers',
           'WorkCreateSerializers', 'WorkDetailSerializers']

from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.shared.translations.sales import ProjectMsg
from ..extend_func import pj_get_alias_permit_from_app
from ..models import Project, ProjectMapMember, ProjectGroups, ProjectWorks
from apps.shared import HRMsg, BaseMsg
from ..models.models import ProjectMapGroup, ProjectMapWork, GroupMapWork


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
        return []

    @classmethod
    def get_works(cls, obj):
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
        ProjectMapGroup.objects.create(project=project, group=group)
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
            'project'
        )


class GroupListSerializers(serializers.ModelSerializer):
    # employee_inherit = serializers.SerializerMethodField()
    #
    # @classmethod
    # def get_employee_inherit(cls, obj):
    #     if obj.employee_inherit:
    #         return obj.employee_inherit_data
    #     return {}

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
        return str(value)

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
