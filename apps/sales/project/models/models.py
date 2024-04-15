__all__ = ['Project', 'ProjectGroups', 'ProjectWorks', 'ProjectMapMember', 'PlanMemberProject', 'ProjectMapGroup',
           'ProjectMapWork', 'GroupMapWork']

import json

from django.utils import timezone

from apps.core.hr.models import PermissionAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel, PROJECT_WORK_STT, \
    PROJECT_WORK_TYPE
from django.db import models


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
                "id": str(self.employee_inherit_id),
                "full_name": self.employee_inherit.get_full_name(),
                "code": self.employee_inherit.code
            }
        return True

    def save(self, *args, **kwargs):
        self.before_save()
        if self.system_status == 1:
            self.code_generator()
            self.system_status = 3
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Project'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProjectGroups(DataAbstractModel):
    works = models.ManyToManyField(
        'project.ProjectGroups',
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
    work_dependencies_style = models.SmallIntegerField(
        choices=PROJECT_WORK_TYPE,
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
        verbose_name = 'Project Team Member'
        verbose_name_plural = 'Project Team Members'
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
