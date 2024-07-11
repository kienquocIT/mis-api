__all__ = ['ProjectCreateBaselineSerializers', 'ProjectBaselineDetailSerializers', 'ProjectBaselineListSerializers',
           'ProjectBaselineUpdateSerializers']

from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.project.models import ProjectBaseline
from apps.sales.project.tasks import create_baseline_data
from apps.shared import ProjectMsg, call_task_background, AbstractDetailSerializerModel, HRMsg


class ProjectBaselineListSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProjectBaseline
        fields = (
            'project_data',
            'member_data',
            'member_perm_data',
            'work_task_data',
            'work_expense_data',
            'baseline_version',
        )


class ProjectCreateBaselineSerializers(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = ProjectBaseline
        fields = (
            'project_data',
            'project',
            'employee_created',
            'employee_inherit_id',
            'system_status'
        )

    @classmethod
    def validate_employee_inherit_id(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})
        return value

    @classmethod
    def validate_project_data(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_CREATE_BASELINE})
        return str(value)

    @decorator_run_workflow
    def create(self, validated_data):
        # create project baseline
        baseline = ProjectBaseline.objects.create(**validated_data)
        call_task_background(
            my_task=create_baseline_data,
            **{
                'baseline_id': str(baseline.id),
                'project_id': str(baseline.project.id)
            }
        )
        return baseline


class ProjectBaselineDetailSerializers(AbstractDetailSerializerModel):

    class Meta:
        model = ProjectBaseline
        fields = (
            'id',
            'system_status',
            'project_data',
            'work_expense_data',
            'work_task_data',
            'member_perm_data',
            'member_data',
            'baseline_version',
        )


class ProjectBaselineUpdateSerializers(AbstractDetailSerializerModel):
    class Meta:
        model = ProjectBaseline
        fields = (
            'id',
            'system_status'
        )

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
