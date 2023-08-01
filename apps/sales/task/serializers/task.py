import re
from datetime import datetime
from django.conf import settings
from rest_framework import serializers
import django.utils.translation

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.sales.opportunity.models import Opportunity
from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus, OpportunityTaskConfig, \
    TaskAttachmentFile

from apps.sales.task.utils import task_create_opportunity_activity_log

from apps.shared import HRMsg, BaseMsg, call_task_background
from apps.shared.translations.sales import SaleTask, SaleMsg

__all__ = ['OpportunityTaskListSerializer', 'OpportunityTaskCreateSerializer', 'OpportunityTaskDetailSerializer',
           'OpportunityTaskUpdateSTTSerializer', 'OpportunityTaskLogWorkSerializer',
           'OpportunityTaskStatusListSerializer', 'OpportunityTaskUpdateSerializer']


class ValidAssignTask:

    @classmethod
    def check_opp_and_return(cls, opp_id):
        is_opp = False
        data = Opportunity.objects.filter(id=opp_id)
        if data.exists():
            data = data.first()
            is_opp = True
        return data, is_opp

    @classmethod
    def check_staffs_in_dept(cls, attrs):
        self_employee = attrs['employee_created']
        assignee = attrs['assign_to']
        if self_employee.group.id == assignee.group.id:
            return True
        return False

    @classmethod
    def check_in_dept_member(cls, attrs):
        assigner = attrs['employee_created']
        assignee = attrs['assign_to']
        employee_group = assigner.group.employee_group.all()
        if employee_group.count():
            for emp in employee_group:
                if emp.id == assignee.id:
                    return True
        return False

    @classmethod
    def check_in_opp_member(cls, opp_data, attrs):
        obj_assignee = attrs['assign_to']
        datas = opp_data.opportunity_sale_team_datas
        for data in datas:
            member = data.get('member')
            if member.id == obj_assignee.id:
                return True
        return False

    @classmethod
    def is_in_opp_check(cls, opt, valid_data):
        obj_opp = valid_data['opportunity']
        opp_data, opp_check = cls.check_opp_and_return(obj_opp.id)
        if not opp_check:
            raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_NOT_EXIST})
        if opt == 1:
            # assign user in opp team
            if len(opp_data.opportunity_sale_team_datas):
                check_in_mem = cls.check_in_opp_member(opp_data, valid_data)
                if not check_in_mem:
                    raise serializers.ValidationError({'detail': SaleTask.ERROR_NOT_IN_MEMBER})
            else:
                raise serializers.ValidationError({'detail': SaleTask.ERROR_TEAM_MEMBER_EMPTY})
        elif opt == 2:
            # assign user staff in dept
            if not cls.check_in_dept_member(valid_data):
                raise serializers.ValidationError({'detail': SaleTask.ERROR_NOT_IN_DEPARTMENT})
        elif opt == 3:
            is_check = cls.check_in_opp_member(opp_data, valid_data)
            if not cls.check_in_dept_member(valid_data) and not is_check:
                raise serializers.ValidationError({'detail': SaleTask.ERROR_1_OR_2_OPT})

    @classmethod
    def is_out_opp_check(cls, opt, attrs):
        if opt == 1:
            is_check = cls.check_in_dept_member(attrs)
            if not is_check:
                raise serializers.ValidationError({'detail': SaleTask.ERROR_NOT_IN_MEMBER})
        if opt == 2:
            is_check = cls.check_staffs_in_dept(attrs)
            if not is_check:
                raise serializers.ValidationError({'detail': SaleTask.ERROR_NOT_STAFF})
        if opt == 3:
            check_01 = cls.check_in_dept_member(attrs)
            check_02 = cls.check_staffs_in_dept(attrs)

            if not check_02 and not check_01:
                raise serializers.ValidationError({'detail': SaleTask.ERROR_1_OR_2_OPT})

    @classmethod
    def check_config(cls, config, validate):
        if config.in_assign_opt > 0 and validate.get('assign_to', None):
            opp = validate.get('opportunity', None)
            if not opp:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_NOT_EXIST})
            cls.is_in_opp_check(config.in_assign_opt, validate)
        elif config.out_assign_opt > 0 and validate.get('assign_to', None):
            cls.is_out_opp_check(config.out_assign_opt, validate)


def handle_attachment(user, instance, attachments, create_method):
    # attachments: list -> danh sách id từ cloud trả về, tạm thời chi có 1 nên lấy [0]
    relate_app = Application.objects.get(id="e66cfb5a-b3ce-4694-a4da-47618f53de4c")
    relate_app_code = 'task'
    instance_id = str(instance.id)
    attachment = attachments[0] if attachments else None
    # check file trong API
    current_attach = TaskAttachmentFile.objects.filter(task=instance)

    # kiểm tra current attach trùng media_id với attachments gửi lên
    if current_attach.exists():
        attach = current_attach.first()
        if not str(attach.media_file) == attachment:
            # this case update new file
            current_attach.delete()
        else:
            # current and update file are the same or attachments is empty
            return True

    if not user.employee_current:
        raise serializers.ValidationError(
            {'User': BaseMsg.USER_NOT_MAP_EMPLOYEE}
        )
    # check file trên cloud
    if not attachment:
        return False
    is_check, attach_check = Files.check_media_file(
        media_file_id=attachment,
        media_user_id=str(user.employee_current.media_user_id)
    )
    if not is_check:
        raise serializers.ValidationError({'Attachment': BaseMsg.UPLOAD_FILE_ERROR})

    # step 1: tạo mới file trong File API
    files = Files.regis_media_file(
        relate_app, instance_id, relate_app_code, user, media_result=attach_check
    )
    # step 2: tạo mới file trong table M2M
    TaskAttachmentFile.objects.create(
        task=instance,
        attachment=files,
        media_file=attachment
    )
    instance.attach = attachments
    if create_method:
        instance.save(update_fields=['attach'])
    return True


class OpportunityTaskListSerializer(serializers.ModelSerializer):
    assign_to = serializers.SerializerMethodField()
    checklist = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()

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

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return {}

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
            'assign_to',
            'checklist',
            'parent_n'
        )


class OpportunityTaskCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=250)

    class Meta:
        model = OpportunityTask
        fields = ('title', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'checklist', 'parent_n', 'remark', 'employee_created', 'log_time',
                  'attach')

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
        raise serializers.ValidationError({'detail': SaleTask.ERROR_ASSIGNER})

    @classmethod
    def validate_parent_n(cls, value):
        if value.parent_n.count():
            raise serializers.ValidationError(
                {'title': django.utils.translation.gettext_lazy("Can not create another sub-task form sub-task")}
            )
        return value

    def validate(self, attrs):
        get_config = OpportunityTaskConfig.objects.filter_current(
            fill__company=True
        )
        if get_config.exists():
            config = get_config.first()
            ValidAssignTask.check_config(config, attrs)
            return attrs
        raise serializers.ValidationError({'detail': SaleTask.ERROR_CONFIG_NOT_FOUND})

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
    assign_to = serializers.SerializerMethodField()
    checklist = serializers.JSONField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    task_log_work = serializers.SerializerMethodField()
    attach = serializers.SerializerMethodField()

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

    @classmethod
    def get_attach(cls, obj):
        if obj.attach:
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

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'remark', 'checklist', 'parent_n', 'employee_created',
                  'task_log_work', 'attach')


class OpportunityTaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'assign_to', 'remark', 'checklist', 'parent_n', 'employee_created', 'attach',
                  'opportunity')

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

    def validate_opportunity(self, attrs):
        before_opp = self.instance.opportunity
        request_emp = self.context.get('employee')
        assign_to = self.initial_data.get('assign_to', None)
        if not before_opp and assign_to and request_emp and str(request_emp) == assign_to:
            raise serializers.ValidationError(
                {'title': django.utils.translation.gettext_lazy(
                    "You do not permission to change Opportunity or Project")}
            )
        return attrs

    @classmethod
    def valid_config_task(cls, current_data, update_data, user):
        employee_request = user.employee_current
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

            # validate follow by config
            if current_data.employee_created == employee_request:
                ValidAssignTask.check_config(config, update_data)
            return True

        raise serializers.ValidationError(
            {'system': django.utils.translation.gettext_lazy("Missing default info please contact with admin.")}
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
