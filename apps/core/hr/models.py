from typing import Union
from uuid import UUID

from django.contrib.auth.models import Permission
from django.db import models
from jsonfield import JSONField

from apps.shared import (
    TenantCoreModel, M2MModel, GENDER_CHOICE, DisperseModel, PermissionCoreModel, TypeCheck,
    CacheCoreModel, call_task_background,
)
from .tasks import reset_cache_employee_n_group


class Employee(TenantCoreModel, PermissionCoreModel, CacheCoreModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=25)

    is_active = models.BooleanField(verbose_name='active status', default=True)
    is_delete = models.BooleanField(verbose_name='delete', default=False)
    search_content = models.CharField(verbose_name='Support Search Content', max_length=300, blank=True, null=True)
    avatar = models.TextField(null=True, verbose_name='avatar path')

    date_joined = models.DateTimeField(verbose_name='joining day', null=True)
    dob = models.DateField(verbose_name='birthday', null=True)
    gender = models.CharField(
        verbose_name='gender male or female',
        choices=GENDER_CHOICE, max_length=6, null=True,
    )

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, null=True)

    space = models.ManyToManyField(
        'space.Space',
        through="SpaceEmployee",
        symmetrical=False,
        blank=True,
        related_name='employee_map_space'
    )

    # plan & application of plan
    # {
    #       '{code_Plan}': [app1, app2, ...]
    # }
    plan_application = JSONField(default={})
    group = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="department",
        related_name="employee_group",
        null=True
    )
    role = models.ManyToManyField(
        'hr.Role',
        through="RoleHolder",
        symmetrical=False,
        blank=True,
        related_name='employee_map_role'
    )
    plan = models.ManyToManyField(
        'base.SubscriptionPlan',
        through="PlanEmployee",
        symmetrical=False,
        blank=True,
        related_name='employee_map_plan'
    )

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def sync_company_map(self, user_id_old, user_id_new, is_new) -> models.Model or Exception:
        if self.company_id:
            company_employee_user_model = DisperseModel(app_model='company_CompanyUserEmployee').get_model()
            if company_employee_user_model:
                if is_new is True:
                    if (
                            hasattr(company_employee_user_model, 'create_new')
                            and hasattr(company_employee_user_model, 'assign_map')
                    ):
                        company_employee_user_model.create_new(self.company_id, self.id, None)
                        if self.user_id:
                            company_employee_user_model.assign_map(self.company_id, self.id, self.user_id)
                        return True
                    raise NotImplementedError("Model company_CompanyUserEmployee sync is not found.")
                else:
                    if user_id_old != user_id_new:
                        if (
                                hasattr(company_employee_user_model, 'remove_map')
                                and hasattr(company_employee_user_model, 'assign_map')
                        ):
                            if user_id_old:
                                company_employee_user_model.remove_map(self.company_id, self.id, user_id_old)
                            if user_id_new:
                                company_employee_user_model.assign_map(self.company_id, self.id, user_id_new)
                            return True
                        raise NotImplementedError(
                            "Model company_CompanyUserEmployee remove_map|assign_map is not found."
                        )
                    else:
                        # by pass when don't change
                        return True
            raise ReferenceError("Get models company_CompanyUserEmployee was returned not found.")
        raise AttributeError('Sync employee to company was raise errors because employee not reference to company.')

    def check_change_user(self):
        original_fields_old = self.get_old_value(
            field_name_list=['user_id'],
        )
        original_fields_new = dict(
            [(field, getattr(self, field)) for field in ['user_id']]
        )
        return original_fields_old['user_id'], original_fields_new['user_id']

    def increment_code(self):
        if not self.code:
            counter = self.__class__.object_global.filter(is_delete=False).count() + 1
            temper = "%04d" % counter
            self.code = f"EMP{temper}"
            return True
        return False

    def save(self, *args, **kwargs):
        # setup full name for search engine
        self.search_content = f'{self.first_name} {self.last_name} , {self.last_name} {self.first_name} , {self.code}'

        # auto create code (temporary)
        self.increment_code()

        # get old user and new user
        user_id_old, user_id_new = None, self.user_id
        if not kwargs.get('force_insert', False):
            user_id_old, user_id_new = self.check_change_user()

        # get old group and new group
        group_id_old = self.get_old_value(
            field_name_list=['group_id'],
        )['group_id']

        # hit DB
        super(Employee, self).save(*args, **kwargs)

        # call sync
        self.sync_company_map(user_id_old, user_id_new, is_new=kwargs.get('force_insert', False))
        self.call_reset_cache(group_id_old)

    def call_reset_cache(self, group_id_old):
        group_id_list = []
        if str(self.group_id) != str(group_id_old):
            if self.group_id:
                group_id_list.append(str(self.group_id))
            if group_id_old:
                group_id_list.append(str(group_id_old))
        elif self.group_id:
            group_id_list.append(str(self.group_id))
        call_task_background(
            reset_cache_employee_n_group,
            [str(self.id)],
            group_id_list,
            countdown=10
        )

    def get_detail(self, excludes=None):
        result = super(Employee, self)._get_detail(excludes=['tenant', 'company'])
        result['first_name'] = self.first_name
        result['last_name'] = self.last_name
        result['email'] = self.email
        result['phone'] = self.phone
        result['is_delete'] = self.is_delete
        result['avatar'] = self.avatar
        return result

    def get_full_name(self, order_arrange=2):
        """
        order_arrange: The ways arrange full name from first_name and last_name
        ---
        First Name: Nguyen Van
        Last Name: A

        Two ways arrange full name:
        [1] {First Name}{Space}{Last Name} <=> Nguyen Van A
        [2] {Last Name}{Point}{Space}{First Name} <=> A. Nguyen Van
        [Another] Return default order_arrange
        """
        if self.last_name or self.first_name:
            if order_arrange == 1:
                return '{}, {}'.format(self.last_name, self.first_name)  # first ways
            return '{} {}'.format(self.last_name, self.first_name)  # second ways or another arrange
        return None

    @classmethod
    def employee_of_group(cls, group_id):
        if group_id and TypeCheck.check_uuid(group_id):
            return [
                str(x) for x in cls.object_normal.filter(group_id=group_id).values_list('id', flat=True)
            ]
        return []

    @property
    def data_cache(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'user_id': str(self.user_id),
            'group_id': str(self.group_id),
            'groups_my_manager': Group.groups_my_manager(employee_id=self.id),
        }


class SpaceEmployee(M2MModel):
    space = models.ForeignKey('space.Space', on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)
    application = JSONField(default=[])

    class Meta:
        verbose_name = 'Space of Employee'
        verbose_name_plural = 'Space of Employee'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class PlanEmployee(M2MModel):
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE
    )
    application = JSONField(default=[])

    class Meta:
        verbose_name = 'Plan of Employee'
        verbose_name_plural = 'Plan of Employee'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Role(TenantCoreModel, PermissionCoreModel):
    abbreviation = models.CharField(
        verbose_name='abbreviation of role (Business analysis -> BA)',
        max_length=10,
        blank=True,
        null=True
    )
    employee = models.ManyToManyField(
        'hr.Employee',
        through="RoleHolder",
        symmetrical=False,
        blank=True,
        related_name='role_map_employee'
    )

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RoleHolder(M2MModel):
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        null=True,
    )

    role = models.ForeignKey(
        'hr.Role',
        on_delete=models.CASCADE,
        null=True,
    )


# Group Level
class GroupLevel(TenantCoreModel):
    level = models.IntegerField(
        verbose_name='group level',
        null=True
    )
    description = models.CharField(
        verbose_name='group level description',
        max_length=500,
        blank=True,
        null=True
    )
    first_manager_description = models.CharField(
        verbose_name='first manager description',
        max_length=500,
        blank=True,
        null=True
    )
    second_manager_description = models.CharField(
        verbose_name='second manager description',
        max_length=500,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Group Level'
        verbose_name_plural = 'Group Levels'
        ordering = ('level',)
        default_permissions = ()
        permissions = ()


# group
class Group(TenantCoreModel, CacheCoreModel):
    group_level = models.ForeignKey(
        'hr.GroupLevel',
        on_delete=models.CASCADE,
        null=True
    )
    parent_n = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="group_parent_n",
        verbose_name="parent group",
        null=True,
    )
    description = models.CharField(
        verbose_name='group description',
        max_length=600,
        blank=True,
        null=True
    )
    group_employee = JSONField(
        verbose_name="group employee",
        null=True,
        default=[]
    )
    first_manager = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="group_first_manager",
        null=True
    )
    first_manager_title = models.CharField(
        verbose_name='first manager title',
        max_length=100,
        blank=True,
        null=True
    )
    second_manager = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="group_second_manager",
        null=True
    )
    second_manager_title = models.CharField(
        verbose_name='second manager title',
        max_length=100,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        verbose_name='active status',
        default=True
    )
    is_delete = models.BooleanField(
        verbose_name='delete',
        default=False
    )

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def groups_my_manager(cls, employee_id: Union[UUID, str]) -> list[str]:
        return [str(x) for x in cls.object_normal.filter(first_manager_id=employee_id).values_list('id', flat=True)]

    @property
    def data_cache(self):
        return {
            'id': str(self.id),
            'group_level_id': str(self.group_level_id),
            'parent_n_id': str(self.parent_n_id),
            'description': self.description,
            'group_employee': self.group_employee,
            'first_manager_id': self.first_manager_id,
            'first_manager_title': self.first_manager_title,
            'second_manager_id': self.second_manager_id,
            'second_manager_title': self.second_manager_title,
            'is_active': self.is_active,
            'is_delete': self.is_delete,
            'all_staff': Employee.employee_of_group(group_id=self.id),
        }

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # get old group and new group
        manager_1st_id_old = self.get_old_value(
            field_name_list=['first_manager_id'],
        )['first_manager_id']
        super(Group, self).save(force_insert, force_update, using, update_fields)
        self.call_reset_cache(manager_1st_id_old)

    def call_reset_cache(self, manager_1st_id_old):
        employee_id_list = []
        if str(self.first_manager_id) != str(manager_1st_id_old):
            if self.first_manager_id:
                employee_id_list.append(str(self.first_manager_id))
            if manager_1st_id_old:
                employee_id_list.append(str(manager_1st_id_old))
        elif self.first_manager_id:
            employee_id_list.append(str(self.first_manager_id))
        call_task_background(
            reset_cache_employee_n_group,
            employee_id_list,
            [str(self.id)],
            countdown=10
        )
