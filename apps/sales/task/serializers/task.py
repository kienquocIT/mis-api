import re
from datetime import datetime
from django.conf import settings
from rest_framework import serializers
import django.utils.translation

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus, OpportunityTaskConfig, \
    TaskAttachmentFile

from apps.sales.task.utils import task_create_opportunity_activity_log

from apps.shared import HRMsg, BaseMsg, call_task_background
from apps.shared.translations.sales import SaleTask, SaleMsg

__all__ = ['OpportunityTaskListSerializer', 'OpportunityTaskCreateSerializer', 'OpportunityTaskDetailSerializer',
           'OpportunityTaskUpdateSTTSerializer', 'OpportunityTaskLogWorkSerializer',
           'OpportunityTaskStatusListSerializer', 'OpportunityTaskUpdateSerializer']


def handle_attachment(user, instance, attachments, create_method):
    if attachments:
        relate_app = Application.objects.get(id="e66cfb5a-b3ce-4694-a4da-47618f53de4c")

        # destroy current attachment
        current_attach = TaskAttachmentFile.objects.filter(task=instance)
        if current_attach:
            current_attach.delete()

        employee_id = getattr(user, 'employee_current_id', None)
        if not employee_id:
            raise serializers.ValidationError({'User': BaseMsg.USER_NOT_MAP_EMPLOYEE})

        # check files
        state, att_objs = Files.check_media_file(file_ids=attachments, employee_id=employee_id, doc_id=instance.id)
        if state:
            # regis file
            file_objs = Files.regis_media_file(
                relate_app=relate_app, relate_doc_id=instance.id, file_objs_or_ids=att_objs,
            )

            # create m2m
            m2m_obj = []
            for counter, obj in enumerate(file_objs):
                m2m_obj.append(
                    TaskAttachmentFile(
                        task=instance,
                        attachment=obj,
                        order=counter+1,
                    )
                )
            TaskAttachmentFile.objects.bulk_create(m2m_obj)

            instance.attach = attachments
            if create_method:
                instance.save(update_fields=['attach'])
            return True
        raise serializers.ValidationError({'Attachment': BaseMsg.UPLOAD_FILE_ERROR})
    return True


class OpportunityTaskListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    checklist = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    child_task_count = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created:
            return {
                'avatar': obj.employee_created.avatar,
                'first_name': obj.employee_created.first_name,
                'last_name': obj.employee_created.last_name,
                'full_name': obj.employee_created.get_full_name()
            }
        return {}

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                'avatar': obj.employee_inherit.avatar,
                'first_name': obj.employee_inherit.first_name,
                'last_name': obj.employee_inherit.last_name,
                'full_name': obj.employee_inherit.get_full_name()
            }
        return {}

    @classmethod
    def get_checklist(cls, obj):
        return obj.checklist if obj.checklist else 0

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

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return {}

    @classmethod
    def get_child_task_count(cls, obj):
        task_list = OpportunityTask.objects.filter_current(
            fill__company=True,
            fill__tenant=True,
            parent_n=obj
        )
        return task_list.count() if task_list else 0

    class Meta:
        model = OpportunityTask
        fields = (
            'id',
            'title',
            'code',
            'task_status',
            'opportunity',
            'start_date',
            'end_date',
            'priority',
            'employee_inherit',
            'checklist',
            'parent_n',
            'employee_created',
            'date_created',
            'child_task_count',
            'percent_completed'
        )


class OpportunityTaskCreateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()
    title = serializers.CharField(max_length=250)

    class Meta:
        model = OpportunityTask
        fields = ('title', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity', 'opportunity_data',
                  'priority', 'label', 'employee_inherit_id', 'checklist', 'parent_n', 'remark', 'employee_created',
                  'log_time', 'attach', 'percent_completed')

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
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            ).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': HRMsg.EMPLOYEES_NOT_EXIST})

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
        raise serializers.ValidationError({'detail': SaleTask.ERROR_ASSIGNER})

    @classmethod
    def validate_parent_n(cls, value):
        if value.parent_n:
            raise serializers.ValidationError(
                {'title': SaleTask.VALID_PARENT_N}
            )
        return value

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            if value.is_close_lost or value.is_deal_close:
                raise serializers.ValidationError(
                    {'opportunity': SaleMsg.OPPORTUNITY_CLOSED}
                )
        return value

    def create(self, validated_data):
        user = self.context.get('user', None)
        task = OpportunityTask.objects.create(**validated_data)
        handle_attachment(user, task, validated_data.get('attach', None), True)
        if task and 'log_time' in validated_data:
            log_time = validated_data['log_time']
            employee = OpportunityTaskLogWorkSerializer.valid_employee_log_work(user.employee_current, task)
            if employee:
                log_time['employee_created'] = employee
                log_time['task'] = task
                OpportunityLogWork.objects.create(**log_time)
        # create activities logs if task has opps code
        if task.opportunity:
            call_task_background(
                my_task=task_create_opportunity_activity_log,
                **{
                    'subject': str(task.title),
                    'opps': str(task.opportunity.id),
                    'task': str(task.id)
                }
            )

        return task


class OpportunityTaskDetailSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    checklist = serializers.JSONField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    task_log_work = serializers.SerializerMethodField()
    attach = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    sub_task_list = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        if obj.employee_inherit:
            return {
                'id': obj.employee_inherit.id,
                'avatar': obj.employee_inherit.avatar,
                'first_name': obj.employee_inherit.first_name,
                'last_name': obj.employee_inherit.last_name,
                'full_name': obj.employee_inherit.get_full_name(),
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
                'last_name': obj.employee_created.last_name,
                'full_name': obj.employee_created.get_full_name(),
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

    @classmethod
    def get_attach(cls, obj):
        if obj.attach:  # noqa
            one_attach = obj.attach[0]
            file = TaskAttachmentFile.objects.filter(
                task=obj,
                media_file=one_attach
            )
            if file.exists():
                # obj.attachments = list((lambda x: x.files, attach))
                attachments = []
                # obj.attachments = list(map(lambda x: x['files'], attach))
                for item in file:
                    files = item.attachment
                    attachments.append(
                        {
                            'files': {
                                "id": str(files.id),
                                "relate_app_id": str(files.relate_app_id),
                                "relate_app_code": files.relate_app_code,
                                "relate_doc_id": str(files.relate_doc_id),
                                "media_file_id": str(files.media_file_id),
                                "file_name": files.file_name,
                                "file_size": int(files.file_size),
                                "file_type": files.file_type
                            }
                        }
                    )
                return attachments
        return []

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': str(obj.opportunity_data['id']),
            'title': obj.opportunity_data['title'],
            'code': obj.opportunity_data['code']
        } if obj.opportunity else {}

    @classmethod
    def get_sub_task_list(cls, obj):
        task_list = OpportunityTask.objects.filter_current(
            fill__company=True,
            fill__tenant=True,
            parent_n=obj
        ).select_related('employee_inherit')
        return [{
            "id": str(sub.id),
            "title": sub.title,
            "employee_inherit": sub.employee_inherit.get_full_name()
        } for sub in task_list] if task_list else []

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity',
                  'priority', 'label', 'employee_inherit', 'remark', 'checklist', 'parent_n', 'employee_created',
                  'task_log_work', 'attach', 'sub_task_list', 'percent_completed')


class OpportunityTaskUpdateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'employee_inherit_id', 'remark', 'checklist', 'parent_n', 'employee_created',
                  'attach', 'opportunity', 'percent_completed')

    @classmethod
    def validate_title(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'title': SaleTask.TITLE_REQUIRED}
        )

    @classmethod
    def validate_task_status(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'status': SaleTask.STT_REQUIRED}
        )

    def validate_opportunity(self, attrs):
        before_opp = self.instance.opportunity
        request_emp = self.context.get('employee')
        assign_to = self.initial_data.get('employee_inherit', None)
        if not before_opp and assign_to and request_emp and str(request_emp) == assign_to:
            raise serializers.ValidationError(
                {'title': SaleTask.ERROR_NOT_CHANGE}
            )

        if attrs.is_close_lost or attrs.is_deal_close:
            raise serializers.ValidationError(
                {'opportunity': SaleMsg.OPPORTUNITY_CLOSED}
            )
        return attrs

    @classmethod
    def valid_config_task(cls, current_data, update_data, user):
        employee_request = user.employee_current
        config = OpportunityTaskConfig.objects.filter_current(
            fill__company=True,
        )
        assignee = update_data['employee_inherit_id']
        if config.exists():
            config = config.first()
            # nếu người gửi là người thụ hưởng và ko phải là người tạo
            if employee_request.id == assignee and not employee_request == current_data.employee_created:
                # cấu hình ko cho update time
                if not config.is_edit_date and (
                        current_data.start_date != update_data['start_date']
                        or current_data.end_date != update_data['end_date']
                ):
                    raise serializers.ValidationError(
                        {
                            'system': SaleTask.ERROR_NOT_LOGWORK
                        }
                    )
                # cấu hình ko cho update estimate
                if not config.is_edit_est and current_data.estimate != update_data['estimate']:
                    raise serializers.ValidationError(
                        {'system': SaleTask.NOT_CHANGE_ESTIMATE}
                    )
            return True
        raise serializers.ValidationError(
            {'system': SaleTask.NOT_CONFIG}
        )

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        opps_before = instance.opportunity
        self.valid_config_task(instance, validated_data, user)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        handle_attachment(user, instance, validated_data.get('attach', None), False)
        instance.save()

        # create activities logs if task has opps code
        if not opps_before and validated_data.get('opportunity', None):
            call_task_background(
                my_task=task_create_opportunity_activity_log,
                **{
                    'subject': str(instance.title),
                    'opps': str(instance.opportunity.id),
                    'task': str(instance.id)
                }
            )
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
                {'task': SaleTask.ERROR_COMPLETE_SUB_TASK}
            )

        raise serializers.ValidationError(
            {'task': SaleTask.ERROR_UPDATE_SUB_TASK}
        )

    @classmethod
    def check_task_complete(cls, instance):
        if OpportunityLogWork.objects.filter(task=instance).count():
            return True
        raise serializers.ValidationError(
            {
                'log time': SaleTask.ERROR_LOGTIME_BEFORE_COMPLETE
            }
        )

    def update(self, instance, validated_data):
        # if task status is COMPLETED
        task_status = validated_data['task_status']
        if task_status.task_kind == 2:
            self.check_sub_task(instance, task_status)
            self.check_task_complete(instance)

        instance.task_status = task_status
        instance.save(update_fields=['task_status', 'percent_completed'])
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
            {'time_spent': SaleTask.ERROR_TIME_SPENT}
        )

    @classmethod
    def valid_employee_log_work(cls, employee, task):
        if employee and task:
            assign_employee = task.employee_inherit
            if employee == assign_employee:
                return employee
        raise serializers.ValidationError(
            {'employee': SaleTask.ERROR_NOT_PERMISSION}
        )

    def create(self, validated_data):
        login_employee = self.context.get('employee', None)
        employee = self.valid_employee_log_work(login_employee, validated_data['task'])
        if employee:
            validated_data['employee_created'] = employee
            log_work = OpportunityLogWork.objects.create(**validated_data)
        else:
            return employee
        return log_work


class OpportunityTaskStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTaskStatus
        fields = ('id', 'title', 'translate_name', 'order', 'task_color')
