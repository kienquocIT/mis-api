import re
from datetime import datetime
from django.conf import settings
from rest_framework import serializers

import django.utils.translation

from apps.core.hr.models import Employee
from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus, OpportunityTaskConfig

__all__ = ['OpportunityTaskListSerializer', 'OpportunityTaskCreateSerializer', 'OpportunityTaskDetailSerializer',
           'OpportunityTaskUpdateSTTSerializer', 'OpportunityTaskLogWorkSerializer',
           'OpportunityTaskStatusListSerializer', 'OpportunityTaskUpdateSerializer']

from apps.shared import HRMsg


class OpportunityTaskListSerializer(serializers.ModelSerializer):
    assign_to = serializers.SerializerMethodField()
    checklist = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()

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

    @classmethod
    def get_task_status(cls, obj):
        if obj.task_status:
            return {
                'id': obj.task_status.id,
                'title': obj.task_status.title,
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
                id=value.id
            )
            if employee.exists():
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
    task_log_work = serializers.SerializerMethodField()

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

    @classmethod
    def get_task_log_work(cls, obj):
        list_log_time = OpportunityLogWork.objects.filter(
            task=obj
        )
        if list_log_time.count():
            list_log_work = [
                {
                    'id': item[0],
                    'start_date': item[1],
                    'end_date': item[2],
                    'time_spent': item[3],
                    'employee_created': {
                        'id': item[4],
                        'first_name': item[5],
                        'last_name': item[6],
                        'avatar': item[7]
                    },
                } for item in list_log_time.values_list(
                    'id', 'start_date', 'end_date', 'time_spent',
                    'employee_created_id',
                    'employee_created__first_name',
                    'employee_created__last_name',
                    'employee_created__avatar'
                )
            ]
            return list_log_work
        return []

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'remark', 'checklist', 'parent_n', 'employee_created',
                  'task_log_work')


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

    @classmethod
    def valid_config_task(cls, current_data, update_data, employee_request):
        config = OpportunityTaskConfig.objects.filter_current(
            fill__company=True,
        )
        assignee = current_data.assign_to
        if config.exists():
            config = config.first()
            # check if request user is assignee user and not is create task/sub-task
            if assignee == employee_request and not current_data.employee_created == employee_request:
                # assignee can not update time
                if not config.is_edit_date and (
                        current_data.start_date != update_data['start_date']
                        or current_data.end_date != update_data['end_date']
                ):
                    raise serializers.ValidationError(
                        {
                            'system': django.utils.translation.gettext_lazy(
                                "You do not permission to change start/end date"
                            )
                        }
                    )
                # assignee can not update estimate
                if not config.is_edit_est and current_data.estimate != update_data['estimate']:
                    raise serializers.ValidationError(
                        {'system': django.utils.translation.gettext_lazy("You do not permission to change estimate")}
                    )
            return True

        raise serializers.ValidationError(
            {'system': django.utils.translation.gettext_lazy("Missing default info please contact with admin.")}
        )

    def update(self, instance, validated_data):
        login_employee = self.context.get('employee', None)
        self.valid_config_task(instance, validated_data, login_employee)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class OpportunityTaskUpdateSTTSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTask
        fields = ('id', 'task_status')

    @classmethod
    def check_sub_task(cls, task, task_stt):
        if task_stt:
            # filter ds sub-task của task update
            task_list = OpportunityTask.objects.filter_current(
                fill__company=True,
                fill__tenant=True,
                parent_n=task
            )
            # kiểm tra xem các sub-task này đã complete hết chưa
            if task_list.count() == task_list.filter(task_status__task_kind=2).count():
                return True
            raise serializers.ValidationError(
                {'task': django.utils.translation.gettext_lazy("Please complete Sub-task before")}
            )

        raise serializers.ValidationError(
            {'task': django.utils.translation.gettext_lazy("Data request is missing please reload and try again.")}
        )

    def update(self, instance, validated_data):
        # if task status is COMPLETED
        task_status = validated_data['task_status']
        if task_status.task_kind == 2:
            self.check_sub_task(instance, task_status)

        instance.task_status = task_status
        instance.save(update_fields=['task_status'])
        return instance


class OpportunityTaskLogWorkSerializer(serializers.ModelSerializer):
    DATETIME = settings.REST_FRAMEWORK['DATETIME_FORMAT']

    class Meta:
        model = OpportunityLogWork
        fields = ('task', 'start_date', 'end_date', 'time_spent', 'employee_created')

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

    @classmethod
    def valid_employee_log_work(cls, employee, task):
        if employee and task:
            assign_employee = task.assign_to
            if employee == assign_employee:
                return employee
        raise serializers.ValidationError(
            {'employee': django.utils.translation.gettext_lazy("You do not permission to log time this task")}
        )

    def create(self, validated_data):
        login_employee = self.context.get('employee', None)
        employee = self.valid_employee_log_work(login_employee, validated_data['task'])
        if employee:
            validated_data['employee_created'] = employee
            log_work = OpportunityLogWork.objects.create(**validated_data)
        return log_work


class OpportunityTaskStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTaskStatus
        fields = ('id', 'title', 'translate_name', 'order', 'task_color')
