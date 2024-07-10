__all__ = ['Project', 'ProjectGroups', 'ProjectWorks', 'ProjectMapMember', 'PlanMemberProject', 'ProjectMapGroup',
           'ProjectMapWork', 'GroupMapWork', 'ProjectBaseline']

import json

from django.utils import timezone
from django.db import models

from apps.core.hr.models import PermissionAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel, PROJECT_WORK_STT, \
    PROJECT_WORK_TYPE


class Project(DataAbstractModel):
    project_owner = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='Representative of project',
        related_name='%(app_label)s_%(class)s_project_owner',
    )
    project_owner_data = models.JSONField(
        default=dict,
        verbose_name='Employee info backup',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': ''}
            ]
        )
    )
    employee_inherit_data = models.JSONField(
        default=dict,
        verbose_name='Project PM info backup',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': ''}
            ]
        )
    )
    start_date = models.DateTimeField(
        verbose_name='Start date',
        default=timezone.now
    )
    finish_date = models.DateTimeField(
        verbose_name='Finish date',
        default=timezone.now
    )
    completion_rate = models.IntegerField(
        verbose_name="Complete rate",
        default=0,
        null=True
    )
    groups = models.ManyToManyField(
        'project.ProjectGroups',
        through='ProjectMapGroup',
        symmetrical=False,
        default=None,
        blank=True,
        related_name='project_map_groups',
    )
    works = models.ManyToManyField(
        'project.ProjectWorks',
        through='ProjectMapWork',
        symmetrical=False,
        default=None,
        blank=True,
        related_name='project_map_works',
    )
    members = models.ManyToManyField(
        'hr.Employee',
        through='ProjectMapMember',
        symmetrical=False,
        through_fields=('project', 'member'),
        blank=True,
        related_name='members_of_project'
    )
    prj_sub_tax_price = models.FloatField(
        help_text='Total price tax of project',
        default=0,
    )
    prj_sub_total = models.FloatField(
        help_text='Total price of project',
        default=0,
    )
    prj_sub_total_after_tax = models.FloatField(
        help_text='Total price after tax',
        default=0,
    )

    def code_generator(self):
        if not self.code:
            asset_return = Project.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                is_delete=False,
                system_status__gte=1
            ).count()
            char = "PJ"
            num_quotient, num_remainder = divmod(asset_return, 1000)
            code = f"{char}{num_remainder + 1:03d}"
            if num_quotient > 0:
                code += f".{num_quotient}"
            self.code = code

    def before_save(self):
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
            }
        if self.project_owner:
            self.project_owner_data = {
                "id": str(self.project_owner_id),
                "full_name": self.project_owner.get_full_name(),
                "code": self.project_owner.code
            }
        return True

    def save(self, *args, **kwargs):
        self.before_save()
        self.code_generator()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Project'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProjectGroups(DataAbstractModel):
    works = models.ManyToManyField(
        'project.ProjectWorks',
        through='GroupMapWork',
        symmetrical=False,
        blank=True,
        related_name='projects_group_map_works',
    )
    employee_inherit_data = models.JSONField(
        default=dict,
        verbose_name='Employee info backup',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': ''}
            ]
        )
    )
    gr_weight = models.FloatField(
        verbose_name='Weight',
        help_text='Weight of group',
        null=True,
        default=0
    )
    gr_rate = models.FloatField(
        verbose_name='Rate',
        help_text='Rate of group',
        null=True,
        default=0
    )
    gr_start_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date start group',
    )
    gr_end_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date end group',
    )
    order = models.SmallIntegerField(
        default=1
    )

    def before_save(self):
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
            }
        return True

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Group of project'
        verbose_name_plural = 'Groups of project'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ProjectWorks(DataAbstractModel):
    tasks = models.ManyToManyField(
        'task.OpportunityTask',
        through='WorkMapTask',
        symmetrical=False,
        default=None,
        blank=True,
        related_name='projects_works_map_tasks',
    )
    work_status = models.SmallIntegerField(
        choices=PROJECT_WORK_STT,
        default=0,
    )
    work_dependencies_type = models.SmallIntegerField(
        choices=PROJECT_WORK_TYPE,
        null=True,
    )
    work_dependencies_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="work_parent",
        verbose_name="parent work",
        null=True,
    )
    employee_inherit_data = models.JSONField(
        default=dict,
        verbose_name='Employee info backup',
        help_text=json.dumps(
            [
                {'id': '', 'full_name': '', 'code': ''}
            ]
        )
    )
    w_weight = models.FloatField(
        verbose_name='Weight',
        help_text='Weight of work',
        null=True,
        default=0
    )
    w_rate = models.FloatField(
        verbose_name='Rate',
        help_text='Rate of work',
        null=True,
        default=0
    )
    w_start_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date start work',
    )
    w_end_date = models.DateTimeField(
        default=timezone.now,
        help_text='Date end work',
    )
    order = models.SmallIntegerField(
        default=1
    )
    expense_data = models.JSONField(
        default=dict,
        verbose_name='total, tax, sub total of expense list in this work',
        help_text=json.dumps(
            {'price': 1000, 'tax': 100, 'total_after_tax': 1100}
        )
    )

    def before_save(self):
        if self.employee_inherit:
            self.employee_inherit_data = {
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
            }
        return True

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Group of work'
        verbose_name_plural = 'Groups of works'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class ProjectMapGroup(DataAbstractModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_project',
    )
    group = models.ForeignKey(
        ProjectGroups,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_group',
    )

    class Meta:
        verbose_name = 'Project map group'
        verbose_name_plural = 'Project map groups'
        default_permissions = ()
        permissions = ()


class ProjectMapWork(DataAbstractModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_project',
    )
    work = models.ForeignKey(
        ProjectWorks,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_work',
    )

    class Meta:
        verbose_name = 'Project map work'
        verbose_name_plural = 'Project map work'
        default_permissions = ()
        permissions = ()


class GroupMapWork(DataAbstractModel):
    group = models.ForeignKey(
        ProjectGroups,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_group',
    )
    work = models.ForeignKey(
        ProjectWorks,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_work',
    )

    class Meta:
        verbose_name = 'Group map work'
        verbose_name_plural = 'Group map work'
        default_permissions = ()
        permissions = ()


class WorkMapTask(DataAbstractModel):
    task = models.ForeignKey(
        'task.OpportunityTask',
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_task',
    )
    work = models.ForeignKey(
        ProjectWorks,
        on_delete=models.CASCADE,
        help_text='',
        related_name='%(app_label)s_%(class)s_work',
    )

    class Meta:
        verbose_name = 'Work map task'
        verbose_name_plural = 'Work map task'
        default_permissions = ()
        permissions = ()


class ProjectMapMember(MasterDataAbstractModel, PermissionAbstractModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_map_member_map_project",
    )
    member = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='Member of Project',
        related_name='project_team_member_member',
    )
    date_modified = models.DateTimeField(
        help_text='Date modified this record in last',
        default=timezone.now,
    )
    permit_view_this_project = models.BooleanField(
        default=False,
        verbose_name='member can view project'
    )
    permit_add_member = models.BooleanField(
        default=False,
        verbose_name='member can add other member but can not set permission for member'
    )
    permit_add_gaw = models.BooleanField(
        default=False,
        verbose_name='member can add group and work'
    )
    permit_app = models.JSONField(
        default=dict,
        help_text=json.dumps(
            {
                'app_id': {
                    'is_create': False,
                    'is_edit': False,
                    'is_view': False,
                    'is_delete': False,
                    'all': False,
                    'belong_to': 0  # 0: user , 1: pro member
                }
            }
        ),
        verbose_name='permission for member in Tenant App'
    )
    plan = models.ManyToManyField(
        'base.SubscriptionPlan',
        through="PlanMemberProject",
        through_fields=('project_member', 'plan'),
        symmetrical=False,
        blank=True,
        related_name='member_pro_map_plan'
    )

    def get_app_allowed(self) -> str:
        return str(self.member_id)

    def sync_parsed_to_main(self):
        ...

    class Meta:
        verbose_name = 'Project team member'
        verbose_name_plural = 'Project team members'
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'company', 'project', 'member')


class PlanMemberProject(SimpleAbstractModel):
    project_member = models.ForeignKey(
        ProjectMapMember,
        on_delete=models.CASCADE,
        related_name='plan_member_project_pj_m'
    )
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE
    )
    application = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Plan of Employee At Project'
        verbose_name_plural = 'Plan of Employee At Project'
        default_permissions = ()
        permissions = ()


class ProjectBaseline(DataAbstractModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_project",
    )
    project_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            {
                "id": "ce0c0422-ffb8-4891-aaf7-c54bc7f17d9a",
                "title": "Kietht edit and update",
                "code": "PJ008",
                "start_date": "2024-07-23 00:00:00",
                "finish_date": "2024-07-27 00:00:00",
                "completion_rate": 0,
                "project_owner": {
                    "id": "ddbaf4ba-1f1a-487f-a37d-b6847c1bf901",
                    "code": "EMP14",
                    "full_name": "Huỳnh Tuấn Kiệt"
                },
                "employee_inherit": {
                    "id": "8b930c65-2794-4904-89db-e7b992f49554",
                    "code": "EMP0004",
                    "full_name": "Hồ Vân Quỳnh"
                },
                "system_status": 1,
                "works": [
                    {
                        "id": "587fc1fb-df7f-4694-883b-4f330ebecb09",
                        "title": "Công việc 01",
                        "work_status": 0,
                        "date_from": "2024-07-02T00:00:00",
                        "date_end": "2024-07-07T00:00:00",
                        "order": 1,
                        "group": "",
                        "relationships_type": None,
                        "dependencies_parent": "",
                        "progress": 0,
                        "weight": 10,
                        "expense_data": {
                            "tax": 100,
                            "price": 1000,
                            "total_after_tax": 1100
                        }
                    }
                ],
                "groups": [],
                "members": [
                    {
                        "id": "ddbaf4ba-1f1a-487f-a37d-b6847c1bf901",
                        "first_name": "Kiệt",
                        "last_name": "Huỳnh Tuấn",
                        "full_name": "Huỳnh Tuấn Kiệt",
                        "email": "ldhoa2002@gmail.com",
                        "avatar": None,
                        "is_active": True
                    }
                ],
                "workflow_runtime_id": None,
                "is_change": False,
                "document_root_id": None,
                "document_change_order": None,
                "status": 200
            }
        ),
        verbose_name='Project data'
    )
    member_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    "id": "ef3ab1bb-e699-4250-ac6d-aefacb77385e",
                    "date_modified": "2024-07-01 09:54:39",
                    "permit_view_this_project": True,
                    "permit_add_member": True,
                    "permit_add_gaw": True,
                    "permission_by_configured": [
                        {
                            "id": "0031870a-db7d-4deb-bba6-a9ea8b713a0c",
                            "edit": True,
                            "view": True,
                            "range": "1",
                            "space": "0",
                            "app_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c",
                            "create": True,
                            "delete": True
                        }
                    ],
                    "status": 200
                },
            ]
        ),
        verbose_name='Member data list'
    )
    member_perm_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            {
                "ef3ab1bb-e699-4250-ac6d-aefacb77385e": [{
                    'id': "ef3ab1bb-e699-4250-ac6d-aefacb77385e",
                    'date_modified': "2024-07-01 09:54:39",
                    'permit_view_this_project': True,
                    'permit_add_member': True,
                    'permit_add_gaw': True,
                    'permission_by_configured': [{
                        "id": "0031870a-db7d-4deb-bba6-a9ea8b713a0c", "edit": True,
                        "view": True, "range": "1", "space": "0",
                        "app_id": "e66cfb5a-b3ce-4694-a4da-47618f53de4c", "create": True,
                        "delete": True
                    }],
                },
                ]
            }
        ),
        verbose_name='Employee perm data list'
    )
    work_task_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    'id': '',
                    'task': {'id': '', 'title': 'lorem ipsum', 'code': 'XX0X'},
                    'work': {'id': '', 'title': 'lorem ipsum', 'code': 'XX0X'},
                    'percent': 0,
                    'assignee': {'id': '', 'full_name': 'Nguyen van A'},
                    'work_before': {'id': '', 'title': 'lorem ipsum', 'code': 'XX0X'},
                }
            ]
        ),
        verbose_name='Work task list'
    )
    work_expense_data = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                {
                    "id": "29801e4c-225b-44a7-b739-a69f84ecc49e",
                    "title": "lorem ipsum dolor sit amet",
                    "expense_name": {},
                    "expense_item": {
                        "id": "90357742-baa9-4a17-a20a-ace15483e111",
                        "title": "Chi phí nhân công phát triển PM"
                    },
                    "uom": {
                        "id": "a16e3b9e-2f4a-442e-bc54-b6ec18569d3c",
                        "title": "Second"
                    },
                    "quantity": 1,
                    "expense_price": 1000,
                    "tax": {
                        "id": "12628b53-7248-4f3b-9ec1-19590a41ecff",
                        "title": "VAT10%",
                        "rate": 10
                    },
                    "sub_total": 1000,
                    "sub_total_after_tax": 1100,
                    "is_labor": False
                },
            ]
        )
    )
    baseline_version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project baseline'
        verbose_name_plural = 'Project baseline'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
