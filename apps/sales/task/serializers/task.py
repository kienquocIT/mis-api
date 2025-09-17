import re
from datetime import datetime
from django.conf import settings
from rest_framework import serializers

from apps.core.attachments.models import update_files_is_approved
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.process.utils import ProcessRuntimeControl
from apps.sales.project.extend_func import check_permit_add_member_pj, calc_update_task, calc_rate_project
from apps.sales.project.models import ProjectMapTasks
from apps.sales.project.tasks import create_project_news
from apps.sales.task.models import OpportunityTask, OpportunityLogWork, OpportunityTaskStatus, OpportunityTaskConfig, \
    TaskAttachmentFile, TaskAssigneeGroup

from apps.shared import HRMsg, ProjectMsg, call_task_background
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.sales import SaleTask, SaleMsg

__all__ = ['OpportunityTaskListSerializer', 'OpportunityTaskCreateSerializer', 'OpportunityTaskDetailSerializer',
           'OpportunityTaskUpdateSTTSerializer', 'OpportunityTaskLogWorkSerializer',
           'OpportunityTaskStatusListSerializer', 'OpportunityTaskUpdateSerializer',
           'OpportunityTaskEmployeeGroupSerializer', 'OpportunityTaskListHasGroupSerializer'
           ]


def handle_attachment(instance, attachment_result):
    if attachment_result and isinstance(attachment_result, dict):
        relate_app = Application.objects.get(id="e66cfb5a-b3ce-4694-a4da-47618f53de4c")
        state = TaskAttachmentFile.resolve_change(
            result=attachment_result, doc_id=instance.id, doc_app=relate_app,
        )
        if state:
            return True
        raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
    return True


def update_models_attachment_assignee(attachment_list):
    attach_lst = list(map(lambda x: str(x.id), attachment_list))
    all_task = TaskAttachmentFile.objects.filter(attachment_id__in=attach_lst)
    all_task.update(is_assignee_file=True)


def map_task_with_project(task, work):
    prj_obj = task.project
    has_prj_map = ProjectMapTasks.objects.filter(project=prj_obj, task=task).exists()
    if prj_obj and has_prj_map is not True:
        ProjectMapTasks.objects.create(
            project=prj_obj,
            member=task.employee_inherit,
            tenant_id=task.tenant_id,
            company_id=task.company_id,
            task=task,
            work_id=str(work) if work else None
        )


class OpportunityTaskListSerializer(serializers.ModelSerializer):
    employee_inherit = serializers.SerializerMethodField()
    checklist = serializers.SerializerMethodField()
    parent_n = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

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
            return obj.employee_inherit.get_detail_minimal()
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
            return obj.opportunity_data
        return {}

    @classmethod
    def get_project(cls, obj):
        if obj.project:
            return obj.project_data
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
            'employee_inherit',
            'checklist',
            'parent_n',
            'employee_created',
            'date_created',
            'child_task_count',
            'percent_completed',
            'project',
        )


class OpportunityTaskCreateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField(allow_null=True, default=None, required=False)
    title = serializers.CharField(max_length=250)
    work = serializers.UUIDField(required=False)
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)
    group_assignee = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=OpportunityTask.get_app_id()
        ) if attrs else None

    class Meta:
        model = OpportunityTask
        fields = (
            'title', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity', 'opportunity_data',
            'priority', 'label', 'employee_inherit_id', 'checklist', 'parent_n', 'remark', 'employee_created',
            'log_time', 'attach', 'attach_assignee', 'percent_completed', 'project', 'work',
            'process', 'process_stage_app', 'group_assignee'
        )

    @classmethod
    def validate_end_time(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError(
            {'title': SaleTask.DATE_TIME_IS_REQUIRED}
        )

    @classmethod
    def validate_employee_inherit_id(cls, attrs):
        return Employee.objects.get_current(
            fill__tenant=True,
            fill__company=True,
            id=attrs
        ).id if attrs else None

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
    def validate_group_assignee(cls, value):
        return TaskAssigneeGroup.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=value
        ).first() if value else None

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

    def validate_attach(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = TaskAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate_attach_assignee(self, attrs):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = TaskAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate(self, attrs):
        if 'project' in attrs:
            prj_obj = attrs['project']
            employee_current = self.context.get('user', None).employee_current
            check_permit = check_permit_add_member_pj(prj_obj, employee_current)
            if check_permit:
                return attrs
            raise serializers.ValidationError({'detail': ProjectMsg.PERMISSION_ERROR})

        if attrs.get('percent_completed', 0) == 100 and not {'start_date', 'end_date', 'time_spent'}.issubset(
                attrs.get('log_time', {})
        ):
            raise serializers.ValidationError({'log time': SaleTask.ERROR_LOGTIME_BEFORE_COMPLETE})

        process_obj = attrs.get('process', None)
        process_stage_app_obj = attrs.get('process_stage_app', None)
        opp_obj = attrs.get('opportunity', None)
        opportunity_id = opp_obj.id if opp_obj else None
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=opportunity_id)

        return attrs

    def create(self, validated_data):
        user = self.context.get('user', None)
        project_work = validated_data.pop('work', None)
        attachment = validated_data.pop('attach', None)
        attach_assignee = validated_data.pop('attach_assignee', None)
        task = OpportunityTask.objects.create(**validated_data)
        if attachment is not None:
            handle_attachment(task, attachment)
        if attach_assignee is not None:
            handle_attachment(task, attach_assignee)
            update_models_attachment_assignee(attach_assignee['new'])
        if task.task_status.is_finish or task.percent_completed == 100:
            update_files_is_approved(
                TaskAttachmentFile.objects.filter(
                    task=task, attachment__is_approved=False
                )
            )
        if task and 'log_time' in validated_data:
            log_time = validated_data['log_time']
            employee = OpportunityTaskLogWorkSerializer.valid_employee_log_work(user.employee_current, task)
            if employee:
                log_time['employee_created'] = employee
                log_time['task'] = task
                OpportunityLogWork.objects.create(**log_time)

        if task.project:
            map_task_with_project(task, project_work)
            calc_update_task(task)
            calc_rate_project(task.project)
            # create news feed
            call_task_background(
                my_task=create_project_news,
                **{
                    'project_id': str(task.project.id),
                    'employee_inherit_id': str(task.employee_inherit.id),
                    'employee_created_id': str(task.employee_created.id),
                    'application_id': str('e66cfb5a-b3ce-4694-a4da-47618f53de4c'),
                    'document_id': str(task.id),
                    'document_title': str(task.title),
                    'title': SaleTask.CREATED_A,
                    'msg': '',
                }
            )

        if task.process:
            ProcessRuntimeControl(process_obj=task.process).register_doc(
                process_stage_app_obj=task.process_stage_app,
                app_id=OpportunityTask.get_app_id(),
                doc_id=task.id,
                doc_title=task.title,
                employee_created_id=task.employee_created_id,
                date_created=task.date_created,
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
    project = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()
    group_assignee = serializers.SerializerMethodField()

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process.id,
                'title': obj.process.title,
                'remark': obj.process.remark,
            }
        return {}

    @classmethod
    def get_process_stage_app(cls, obj):
        if obj.process_stage_app:
            return {
                'id': obj.process_stage_app.id,
                'title': obj.process_stage_app.title,
                'remark': obj.process_stage_app.remark,
            }
        return {}

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
        att_objs = TaskAttachmentFile.objects.select_related('attachment').filter(task=obj)
        lst = []
        for item in att_objs:
            f_detail = item.attachment.get_detail()
            f_detail['is_assignee_file'] = item.is_assignee_file
            lst.append(f_detail)
        return lst

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': str(obj.opportunity_data['id']),
            'title': obj.opportunity_data['title'],
            'code': obj.opportunity_data['code']
        } if obj.opportunity else {}

    @classmethod
    def get_project(cls, obj):
        return {
            'id': str(obj.project_data['id']),
            'title': obj.project_data['title'],
            'code': obj.project_data['code']
        } if obj.project else {}

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

    @classmethod
    def get_group_assignee(cls, obj):
        return {
            'id': str(obj.group_assignee.id),
            'title': obj.group_assignee.title
        } if obj.group_assignee else {}

    class Meta:
        model = OpportunityTask
        fields = (
            'id',
            'title',
            'code',
            'task_status',
            'start_date',
            'end_date',
            'estimate',
            'opportunity',
            'priority',
            'label',
            'employee_inherit',
            'remark',
            'checklist',
            'parent_n',
            'employee_created',
            'task_log_work',
            'attach',
            'sub_task_list',
            'percent_completed',
            'project',
            'process',
            'process_stage_app',
            'group_assignee',
        )


class OpportunityTaskUpdateSerializer(serializers.ModelSerializer):
    employee_inherit_id = serializers.UUIDField(allow_null=True, required=False)
    group_assignee = serializers.UUIDField(allow_null=True, required=False)
    work = serializers.UUIDField(required=False)
    task_status = serializers.UUIDField(allow_null=True, required=False)
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = OpportunityTask
        fields = ('id', 'title', 'code', 'task_status', 'start_date', 'end_date', 'estimate', 'opportunity_data',
                  'priority', 'label', 'employee_inherit_id', 'remark', 'checklist', 'parent_n', 'employee_created',
                  'attach', 'attach_assignee', 'opportunity', 'percent_completed', 'project', 'work', 'group_assignee')

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
    def validate_group_assignee(cls, attrs):
        return TaskAssigneeGroup.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id=attrs
        ).first() if attrs else None

    @classmethod
    def valid_config_task(cls, current_data, update_data, user):
        employee_request = user.employee_current
        config = OpportunityTaskConfig.objects.filter_on_company()
        assignee = update_data['employee_inherit_id']
        if config.exists():
            config = config.first()
            # nếu user nằm trong group assign và phiếu đang có người thụ hưởng là trống
            if str(assignee) in current_data.group_assignee.employee_list_access \
                    and current_data.employee_inherit is None and len(update_data) == 2 and (
                    'employee_inherit_id' in update_data and 'employee_modified_id' in update_data):
                return True

            # nếu người gửi là người thụ hưởng và ko phải là người tạo
            if employee_request.id == assignee and not employee_request == current_data.employee_created:
                # cấu hình ko cho update time
                if not config.is_edit_date and (current_data.start_date != update_data['start_date']
                                                or current_data.end_date != update_data['end_date']):
                    raise serializers.ValidationError({'system': SaleTask.ERROR_NOT_LOGWORK})
                # cấu hình ko cho update estimate
                if not config.is_edit_est and current_data.estimate != update_data['estimate']:
                    raise serializers.ValidationError({'system': SaleTask.NOT_CHANGE_ESTIMATE})
            # group có bị thay đổi ko và ng update group phải nằm trong danh sách được cấp quyền trong config
            if update_data['group_assignee'] is not None and hasattr(current_data, 'group_assignee'):
                if update_data['group_assignee'] != current_data['group_assignee'] and \
                        employee_request.id not in config.user_allow_group_handle:
                    raise serializers.ValidationError({'group_assignee': SaleTask.ASSIGNEE_GROUP_NOT_PERMISSION})
            return True
        raise serializers.ValidationError({'system': SaleTask.NOT_CONFIG})

    def validate_attach(self, attrs):
        user = self.context.get('user', None)
        instance = self.instance
        if user and hasattr(user, 'employee_current_id'):
            state, result = TaskAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate_attach_assignee(self, attrs):
        user = self.context.get('user', None)
        instance = self.instance
        if user and hasattr(user, 'employee_current_id'):
            state, result = TaskAttachmentFile.valid_change(
                current_ids=attrs, employee_id=user.employee_current_id, doc_id=instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    def validate(self, attrs):
        if 'project' in attrs:
            employee_current = self.context.get('user', None).employee_current
            check_permit = check_permit_add_member_pj(attrs['project'], employee_current)
            # nếu user chỉ update
            if str(self.instance.project.id) == str(attrs['project'].id) and str(
                    self.instance.employee_inherit.id
            ) == str(employee_current.id):
                check_permit = True
            if self.instance.project.project_status == 4:
                check_permit = False
            if check_permit:
                return attrs
            raise serializers.ValidationError({'detail': ProjectMsg.PERMISSION_ERROR})
        return attrs

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        self.valid_config_task(instance, validated_data, user)
        attachment = validated_data.pop('attach', None)
        attach_assignee = validated_data.pop('attach_assignee', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if attachment is not None:
            handle_attachment(instance, attachment)
        if attach_assignee is not None:
            handle_attachment(instance, attach_assignee)
            if len(attach_assignee['new']):
                update_models_attachment_assignee(attach_assignee['new'])

        if instance.project:
            project_work = validated_data.pop('work', None)
            map_task_with_project(instance, project_work)
            calc_update_task(instance)
            calc_rate_project(instance.project)
            # create news feed
            call_task_background(
                my_task=create_project_news,
                **{
                    'project_id': str(instance.project.id),
                    'employee_inherit_id': str(instance.employee_inherit.id),
                    'employee_created_id': str(instance.employee_created.id),
                    'application_id': str('e66cfb5a-b3ce-4694-a4da-47618f53de4c'),
                    'document_id': str(instance.id),
                    'document_title': str(instance.title),
                    'title': SaleTask.UPDATED_A,
                    'msg': '',
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
        fields = ('id', 'title', 'translate_name', 'order', 'task_color', 'is_finish')


class OpportunityTaskEmployeeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssigneeGroup
        fields = ('id', 'title', 'employee_list_access')

    def create(self, validated_data):
        group = TaskAssigneeGroup.objects.create(**validated_data)
        return group


class OpportunityTaskListHasGroupSerializer(OpportunityTaskListSerializer):
    group_assignee = serializers.SerializerMethodField()

    @classmethod
    def get_group_assignee(cls, obj):
        return {
            'id': str(obj.group_assignee.id),
            'tile': obj.group_assignee.title
        } if obj.group_assignee else {}

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
            'percent_completed',
            'project',
            'group_assignee'
        )
