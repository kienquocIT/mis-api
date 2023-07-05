import re
from datetime import datetime
from django.conf import settings
from rest_framework import serializers

import django.utils.translation

from apps.core.hr.models import Employee
from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus

__all__ = ['OpportunityTaskListSerializer', 'OpportunityTaskCreateSerializer', 'OpportunityTaskDetailSerializer',
           'OpportunityTaskUpdateSTTSerializer', 'OpportunityTaskLogWorkSerializer',
           'OpportunityTaskStatusListSerializer', 'OpportunityTaskUpdateSerializer']

from apps.shared import HRMsg


class OpportunityTaskListSerializer(serializers.ModelSerializer):
    assign_to = serializers.SerializerMethodField()
    checklist = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()

    @classmethod
    def get_assign_to(cls, obj):
        if obj.assign_to:
            return {
                'avatar': obj.assign_to.avatar,
                'first_name': obj.assign_to.first_name,
                'last_name': obj.assign_to.last_name
            }
        return {}

    @classmethod
    def get_checklist(cls, obj):
        if obj.checklist:
            return obj.checklist
        return 0

    @classmethod
    def get_parent_n(cls, obj):
        if obj.parent_n:
            return {
                'id': obj.parent_n.id,
                'title': obj.parent_n.title,
                'code': obj.parent_n.code
            }
        return {}

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'end_date', 'priority', 'assign_to', 'checklist', 'parent_n')


class OpportunityTaskCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=250)

    class Meta:
        model = OpportunityTask
        fields = ('title', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'checklist', 'parent_n', 'remark', 'employee_created')

    @classmethod
    def validate_title(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'title': django.utils.translation.gettext_lazy("Title is required.")}
        )

    @classmethod
    def validate_end_time(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'title': django.utils.translation.gettext_lazy("End date is required.")}
        )

    @classmethod
    def validate_employee_created(cls, value):
        if value:
            employee = Employee.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=value.employee_created_id
            ).count()
            if employee == len(value):
                return value
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'detail': 'Assigner not found'})

    def create(self, validated_data):
        task = OpportunityTask.objects.create(**validated_data)
        return task


class OpportunityTaskDetailSerializer(serializers.ModelSerializer):
    assign_to = serializers.SerializerMethodField()
    checklist = serializers.JSONField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    @classmethod
    def get_assign_to(cls, obj):
        if obj.assign_to:
            return {
                'id': obj.assign_to.id,
                'avatar': obj.assign_to.avatar,
                'first_name': obj.assign_to.first_name,
                'last_name': obj.assign_to.last_name
            }
        return {}

    @classmethod
    def get_checklist(cls, obj):
        if obj.checklist:
            return obj.checklist
        return 0

    @classmethod
    def get_parent_n(cls, obj):
        if obj.parent_n:
            return {
                'id': obj.parent_n.id,
                'title': obj.parent_n.title,
                'code': obj.parent_n.code
            }
        return {}

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return {
                'id': obj.employee_created.id,
                'first_name': obj.employee_created.first_name,
                'last_name': obj.employee_created.last_name
            }
        return {}

    @classmethod
    def get_task_status(cls, obj):
        if obj.task_status:
            return {
                'id': obj.task_status.id,
                'title': obj.task_status.title,
                'translate_name': obj.task_status.translate_name
            }
        return {}

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'remark', 'checklist', 'parent_n', 'employee_created')


class OpportunityTaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'remark', 'checklist', 'parent_n', 'employee_created')

    @classmethod
    def validate_title(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'title': django.utils.translation.gettext_lazy("Title is required.")}
        )

    @classmethod
    def validate_task_status(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'title': django.utils.translation.gettext_lazy("Status is required.")}
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class OpportunityTaskUpdateSTTSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTask
        fields = ('id', 'task_status')

    def update(self, instance, validated_data):
        instance.task_status = validated_data['task_status']
        instance.save(update_fields=['task_status'])
        return instance


class OpportunityTaskLogWorkSerializer(serializers.ModelSerializer):
    DATETIME = settings.REST_FRAMEWORK['DATETIME_FORMAT']

    class Meta:
        model = OpportunityLogWork
        fields = ('task', 'start_date', 'end_date', 'time_spent', 'employee_created')

    # @classmethod
    # def validate_task(cls, value):
    #     try:
    #         task = OpportunityTask.objects.get(id=value)
    #         if task:
    #             return value
    #     except OpportunityTask.DoesNotExist:
    #         raise serializers.ValidationError({'plan': _("Task not found")})

    @classmethod
    def validate_start_date(cls, attrs):
        if isinstance(attrs, datetime):
            return datetime.strftime(attrs, cls.DATETIME) if attrs else None
        return str(attrs)

    @classmethod
    def validate_end_date(cls, attrs):
        if isinstance(attrs, datetime):
            return datetime.strftime(attrs, cls.DATETIME) if attrs else None
        return str(attrs)

    @classmethod
    def validate_time_spent(cls, attrs):
        pattern = r'^\d+(?:\.\d+)?[dhm]$'
        input_string = attrs
        match = re.match(pattern, input_string)
        if match:
            return str(input_string)
        raise serializers.ValidationError(
            {'time_spent': django.utils.translation.gettext_lazy("Time spent is wrong format.")}
        )

    def create(self, validated_data):
        employee = self.context.get('employee', None)
        if employee:
            validated_data['employee_created'] = employee
        log_work = OpportunityLogWork.objects.create(**validated_data)
        return log_work


class OpportunityTaskStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTaskStatus
        fields = ('id', 'title', 'translate_name', 'order')
