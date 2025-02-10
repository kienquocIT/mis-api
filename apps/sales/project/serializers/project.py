__all__ = ['ProjectListSerializers', 'ProjectCreateSerializers', 'ProjectDetailSerializers', 'ProjectUpdateSerializers',
           'ProjectUpdateOrderSerializers', 'ProjectUpdateStatusSerializers']

import json
from datetime import datetime

from rest_framework import serializers
from django.utils import timezone

from apps.core.process.utils import ProcessRuntimeControl
from apps.shared import HRMsg, FORMATTING, ProjectMsg
from ..extend_func import pj_get_alias_permit_from_app
from ..models import Project, ProjectMapMember, ProjectWorks, ProjectGroups, WorkMapExpense, ProjectConfig
from ...task.models import TaskAttachmentFile


class ProjectListSerializers(serializers.ModelSerializer):
    works = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    project_pm = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    baseline = serializers.SerializerMethodField()

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
        if obj.employee_inherit_data:
            return obj.employee_inherit_data
        return {}

    @classmethod
    def get_project_pm(cls, obj):
        if obj.project_pm_data:
            return obj.project_pm_data
        return {}

    @classmethod
    def get_baseline(cls, obj):
        baseline = {
            'project_data': [],
            'count': 0,
            'new_t_month': 0
        }
        lst_prj = obj.project_projectbaseline_project_related.all()
        if lst_prj:
            crt = datetime.now()
            for item in lst_prj:
                project_data = item.project_data
                if not isinstance(project_data, dict):
                    project_data = json.loads(project_data)
                baseline['project_data'].append({
                    'id': str(item.id),
                    'code': project_data['code'],
                    'title': project_data['title'],
                    'project_pm': project_data['employee_inherit'],
                    'start_date': project_data['start_date'],
                    'finish_date': project_data['finish_date'],
                    'completion_rate': project_data['completion_rate'],
                    'works': {
                        'all': len(project_data['work']),
                        'completed': len([x for x in project_data['work'] if x['progress'] == 100])
                    },
                    'tasks': {
                        'all': len(item.work_task_data),
                        'completed': len([x for x in item.work_task_data if x['percent'] == 100])
                    },
                    'version': item.baseline_version,
                    'system_status': item.system_status
                })
                baseline['count'] += 1
                if item.date_created.year == crt.year and item.date_created.month == crt.month:
                    baseline['new_t_month'] += 1

            return baseline
        return baseline

    @classmethod
    def get_system_status(cls, obj):
        if obj:
            return obj.project_status
        return ''

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'code',
            'project_pm',
            'employee_inherit',
            'start_date',
            'finish_date',
            'completion_rate',
            'works',
            'tasks',
            'system_status',
            'baseline',
            'date_created',
            'date_close'
        )


class ProjectCreateSerializers(serializers.ModelSerializer):
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def create_project_map_member(cls, project):
        permission_by_configured = pj_get_alias_permit_from_app(employee_obj=project.employee_inherit)
        ProjectMapMember.objects.create(
            tenant_id=project.tenant_id,
            company_id=project.company_id,
            project=project,
            member=project.employee_inherit,
            permit_add_member=True,
            permit_add_gaw=True,
            permit_lock_fd=True,
            permit_view_this_project=True,
            permission_by_configured=permission_by_configured
        )
        if project.project_pm:
            if str(project.employee_inherit_id) != str(project.project_pm.id):
                permission_by_configured_pm = pj_get_alias_permit_from_app(employee_obj=project.project_pm)
                ProjectMapMember.objects.create(
                    tenant_id=project.tenant_id,
                    company_id=project.company_id,
                    project=project,
                    member=project.project_pm,
                    permit_add_member=True,
                    permit_add_gaw=True,
                    permit_lock_fd=True,
                    permit_view_this_project=True,
                    permission_by_configured=permission_by_configured_pm
                )

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=Project.get_app_id()
        ) if attrs else None

    def validate(self, attrs):
        process_obj = attrs.get('process', None)
        process_stage_app_obj = attrs.get('process_stage_app', None)
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(process_stage_app_obj=process_stage_app_obj, opp_id=None)
        return attrs

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)
        # create project team member
        self.create_project_map_member(project)

        if project.process:
            ProcessRuntimeControl(process_obj=project.process).register_doc(
                process_stage_app_obj=project.process_stage_app,
                app_id=Project.get_app_id(),
                doc_id=project.id,
                doc_title=project.title,
                employee_created_id=project.employee_created_id,
                date_created=project.date_created,
            )

        return project

    class Meta:
        model = Project
        fields = (
            'title',
            'project_pm',
            'start_date',
            'finish_date',
            'system_status',
            'employee_inherit',
            'process', 'process_stage_app',
        )


class ProjectDetailSerializers(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    works = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    project_pm = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()
    assignee_attachment = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

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
                    "expense_data": item.work.expense_data,
                    "bom_data": item.work.bom_data
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
            return sorted(works_list, key=lambda key: (key['order'], key['order']))
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
    def get_project_pm(cls, obj):
        if obj.project_pm:
            return obj.project_pm_data
        return {}

    def get_system_status(self, obj):
        if obj:
            return self.instance.project_status
        return ''

    @classmethod
    def get_assignee_attachment(cls, obj):
        lst_task = obj.project_projectmaptasks_project.all()
        lst = []
        if lst_task.exists():
            for obj_proj in lst_task:
                att_objs = TaskAttachmentFile.objects.select_related('attachment').filter(task=obj_proj.task)
                if att_objs.exists():
                    for item in att_objs:
                        f_detail = item.attachment.get_detail()
                        f_detail['is_assignee_file'] = item.is_assignee_file
                        lst.append(f_detail)
        return lst

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

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'code',
            'start_date',
            'finish_date',
            'date_close',
            'completion_rate',
            'project_pm',
            'employee_inherit',
            'system_status',
            'works',
            'groups',
            'members',
            'assignee_attachment',
            'process', 'process_stage_app',
            'finish_date_lock',
        )


class ProjectUpdateSerializers(serializers.ModelSerializer):
    expense_data = serializers.JSONField(required=False)
    work_expense_data = serializers.JSONField(required=False)
    delete_expense_lst = serializers.JSONField(required=False)
    finish_date_lock = serializers.BooleanField(required=False)

    @classmethod
    def validate_project_pm(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_employee_inherit(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_NOT_EXIST})
        return value

    @classmethod
    def validate_expense_data(cls, value):
        return value

    def validate_finish_date(self, attrs):
        groups = self.instance.project_projectmapgroup_project.all()
        for item in groups:
            if item.group.gr_end_date > attrs:
                raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_FINISH_DATE_INVALID_CASE1})
        works = self.instance.project_projectmapwork_project.all()
        for item in works:
            if item.work.w_end_date > attrs:
                raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_FINISH_DATE_INVALID_CASE1})
        return attrs

    def validate_finish_date_lock(self, attrs):
        is_permit_update = self.context.get('has_permit_update_lock', None)
        if is_permit_update is not True:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_LOCK_PERMIT_DENIED})
        return attrs

    class Meta:
        model = Project
        fields = (
            'title',
            'finish_date',
            'project_pm',
            'employee_inherit',
            'system_status',
            'expense_data',
            'work_expense_data',
            'delete_expense_lst',
            'finish_date_lock'
        )

    @classmethod
    def delete_expense_map_list(cls, lst):
        if lst:
            WorkMapExpense.objects.filter(id__in=lst).delete()

    def cu_expense_lst(self, lst):
        if lst:
            create_lst = []
            delete_lst = []
            for idx in lst:
                dict_item = lst[idx]
                for item in dict_item:
                    if 'id' in item:
                        delete_lst.append(item['id'])
                        create_lst.append(WorkMapExpense(
                            id=item['id'],
                            tenant_id=self.instance.tenant_id,
                            company_id=self.instance.company_id,
                            work_id=idx,
                            title=item['title'],
                            expense_name_id=item['expense_name']['id'] if isinstance(
                                item['expense_name'], dict) and 'id' in item['expense_name'] else None,
                            expense_item_id=item['expense_item']['id'],
                            uom_id=item['uom']['id'],
                            quantity=item['quantity'],
                            expense_price=item['expense_price'],
                            tax_id=item['tax']['id'] if 'id' in item['tax'] else None,
                            sub_total=item['sub_total'],
                            sub_total_after_tax=item['sub_total_after_tax'],
                            is_labor=item['is_labor'],
                            is_service=item['is_service']
                        ))
                    else:
                        create_lst.append(WorkMapExpense(
                            tenant_id=self.instance.tenant_id,
                            company_id=self.instance.company_id,
                            work_id=idx,
                            title=item['title'],
                            expense_name_id=item['expense_name']['id'] if isinstance(
                                item['expense_name'], dict) and 'id' in item['expense_name'] else None,
                            expense_item_id=item['expense_item']['id'],
                            uom_id=item['uom']['id'],
                            quantity=item['quantity'],
                            expense_price=item['expense_price'],
                            tax_id=item['tax']['id'] if 'id' in item['tax'] else None,
                            sub_total=item['sub_total'],
                            sub_total_after_tax=item['sub_total_after_tax'],
                            is_labor=item['is_labor'],
                            is_service=item['is_service']
                        ))
            if delete_lst:
                WorkMapExpense.objects.filter(id__in=delete_lst).delete()
            WorkMapExpense.objects.bulk_create(create_lst)

    @classmethod
    def update_work_expense(cls, lst):
        if lst:
            for item in lst:
                work_expense = lst[item]
                ProjectWorks.objects.filter(id=item).update(expense_data=work_expense)

    def update(self, instance, validated_data):
        expense_lst = validated_data.pop('expense_data', None)
        work_expense_lst = validated_data.pop('work_expense_data', None)
        delete_expense_lst = validated_data.pop('delete_expense_lst', None)
        system_status = validated_data.pop('system_status', None)
        if system_status == 2 and instance.project_status != 3:
            # re-open project
            validated_data['project_status'] = instance.prev_status
            instance.date_close = None
        elif system_status == 3:
            # complete project
            validated_data['prev_status'] = instance.project_status
            # ngày finish nhỏ hơn ngày hiện tại
            if instance.finish_date < timezone.now():
                instance.date_close = timezone.now()
        elif system_status == 4:
            # closed project
            validated_data['project_status'] = system_status
            instance.date_close = timezone.now()
        # - delete all expense(user delete)
        # - create and update
        # - update work info
        self.delete_expense_map_list(delete_expense_lst)
        self.cu_expense_lst(expense_lst)
        self.update_work_expense(work_expense_lst)

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


class ProjectUpdateStatusSerializers(serializers.ModelSerializer):
    system_status = serializers.IntegerField()

    def validate_system_status(self, value):
        if not value:
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_STATUS_ERROR})

        tenant = self.context.get('tenant', None)
        company = self.context.get('company', None)
        user = self.context.get('employee', None)
        user_edited = ProjectConfig.objects.filter(
            tenant=tenant, company=company, person_can_end__contains=str(user.id)
        )
        if not user_edited.exists():
            raise serializers.ValidationError({'detail': ProjectMsg.PROJECT_CLOSE_PROJECT_ERROR})
        return value

    class Meta:
        model = Project
        fields = (
            'system_status',
        )

    def update(self, instance, validated_data):
        system_status = validated_data.pop('system_status', None)
        instance.date_close = None
        if system_status == 2:
            # re-open project
            validated_data['project_status'] = instance.prev_status
            instance.date_close = None
        elif system_status == 3:
            # complete project
            # ngày finish nhỏ hơn ngày hiện tại
            if instance.finish_date < timezone.now():
                instance.date_close = timezone.now()
        elif system_status == 4:
            # closed project
            validated_data['prev_status'] = instance.project_status
            validated_data['project_status'] = system_status
            instance.date_close = timezone.now()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
