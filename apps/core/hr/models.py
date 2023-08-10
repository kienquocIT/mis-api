from typing import Union, TypedDict
from uuid import UUID

from django.conf import settings
from django.db import models

from apps.core.models import TenantAbstractModel
from apps.shared import (
    SimpleAbstractModel,
    DisperseModel,
    GENDER_CHOICE, TypeCheck, MediaForceAPI,
)


class PermOption(TypedDict, total=False):
    option: int


class PermissionAbstractModel(models.Model):
    # by ID
    permission_by_id_sample = {
        'hrm': {
            'employee': {
                'create': ['{id}'], 'view': ['{id}'], 'edit': ['{id}'], 'delete': ['{id}']
            }
        },
    }
    permission_by_id = models.JSONField(default=dict, verbose_name='Special Permissions with ID Doc')

    # by be configured
    permission_by_configured_sample = [
        {
            "id": "e388f95e-457b-4cf6-8689-0171e71fa58f",
            "app_id": "50348927-2c4f-4023-b638-445469c66953",
            "app_data": {
                "id": "50348927-2c4f-4023-b638-445469c66953", "title": "Employee", "code": "employee"
            },
            "plan_id": "395eb68e-266f-45b9-b667-bd2086325522",
            "plan_data": {"id": "395eb68e-266f-45b9-b667-bd2086325522", "title": "HRM", "code": "hrm"},
            "create": True, "view": True, "edit": False, "delete": False, "range": "4",
        }
    ]
    permission_by_configured = models.JSONField(
        default=list, verbose_name='Permissions was configured by Administrator'
    )

    # as sum data permissions
    permissions_parsed_sample = {
        '': {
            'hrm': {
                'employee': {
                    'create': {
                        '4': {},
                    }, 'view': {'4': {}}, 'edit': {'4': {}}, 'delete': {'4': {}}
                }
            },
            'sale': {'account': {'view': {'4': {}}}}
        },
        '{space_code}': {},
    }
    permissions_parsed = models.JSONField(default=dict, verbose_name='Data was parsed')

    # summary keys
    permission_keys = ('permission_by_id', 'permission_by_configured')

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Employee(TenantAbstractModel, PermissionAbstractModel):
    code = models.CharField(max_length=25, blank=True)

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
    plan_application = models.JSONField(default=dict)
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

    # media
    media_user_id = models.UUIDField(null=True)
    media_refresh_token = models.TextField(blank=True)
    media_refresh_token_expired = models.DateTimeField(null=True)
    media_access_token = models.TextField(blank=True)
    media_access_token_expired = models.DateTimeField(null=True)
    media_username = models.TextField(blank=True)
    media_password = models.TextField(blank=True)
    media_avatar_hash = models.TextField(blank=True)

    is_admin_company = models.BooleanField(
        default=False,
        verbose_name='Is Admin Company',
    )

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee'
        ordering = ('-date_created',)
        unique_together = ('company', 'code', 'is_delete')
        default_permissions = ()
        permissions = ()

    def __str__(self):
        return self.first_name + '. ' + self.last_name

    def sync_company_map(self, user_id_old, user_id_new, is_new) -> models.Model or Exception:
        if self.company_id:  # pylint: disable=R1702
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
                return True
            raise ReferenceError("Get models company_CompanyUserEmployee was returned not found.")
        raise AttributeError('Sync employee to company was raise errors because employee not reference to company.')

    def check_change_user(self):
        original_fields_old = self.get_old_value(
            field_name_list=['user_id'],
        )
        original_fields_new = {
            field: getattr(self, field) for field in ['user_id']
        }
        return original_fields_old['user_id'], original_fields_new['user_id']

    def increment_code(self):
        if not self.code:
            counter = self.__class__.objects.filter(is_delete=False).count() + 1
            temper = "%04d" % counter  # pylint: disable=C0209
            self.code = f"EMP{temper}"
            return True
        return False

    def save(self, *args, **kwargs):
        # setup full name for search engine
        self.search_content = f'{self.first_name} {self.last_name} , {self.last_name} {self.first_name} , {self.code}'

        # auto create code (temporary)
        employee = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "EMP"
        if not self.code:
            temper = "%04d" % (employee + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

        # get old user and new user
        user_id_old, user_id_new = None, self.user_id
        if not kwargs.get('force_insert', False):
            user_id_old, user_id_new = self.check_change_user()

        # hit DB
        super().save(*args, **kwargs)

        # call sync
        self.sync_company_map(user_id_old, user_id_new, is_new=kwargs.get('force_insert', False))
        if kwargs.get('force_insert', False) and not self.media_user_id and settings.ENABLE_PROD is True:
            MediaForceAPI.call_sync_employee(self)

    def get_detail_minimal(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'avatar': self.media_avatar_hash,
        }

    def get_detail(self, *args):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'email': self.email,
            'phone': self.phone,
            'is_delete': self.is_delete,
            'avatar': self.avatar,
            'media_avatar_hash': self.media_avatar_hash,
        }

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
                return f'{self.last_name}, {self.first_name}'  # first ways
            return f'{self.last_name} {self.first_name}'  # second ways or another arrange
        return None

    @classmethod
    def employee_of_group(cls, group_id):
        if group_id and TypeCheck.check_uuid(group_id):
            return [
                str(x) for x in cls.objects.filter(group_id=group_id).values_list('id', flat=True)
            ]
        return []


class SpaceEmployee(SimpleAbstractModel):
    space = models.ForeignKey('space.Space', on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)
    application = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Space of Employee'
        verbose_name_plural = 'Space of Employee'
        default_permissions = ()
        permissions = ()


class PlanEmployee(SimpleAbstractModel):
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE
    )
    application = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Plan of Employee'
        verbose_name_plural = 'Plan of Employee'
        default_permissions = ()
        permissions = ()


# role | job position
class Role(TenantAbstractModel, PermissionAbstractModel):
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
    plan = models.ManyToManyField(
        'base.SubscriptionPlan',
        through="PlanRole",
        symmetrical=False,
        blank=True,
        related_name='role_map_plan',
    )

    def sync_plan_app(self, plan_app_data_dict):
        ids_valid = []
        for obj in PlanRole.objects.filter(plan_id__in=plan_app_data_dict.keys(), role=self):
            data = plan_app_data_dict.get(str(obj.plan_id), None)
            if data:
                ids_valid.append(str(obj.plan_id))
                obj.application = data['application']
                obj.application_m2m.clear()
                for app_id in data['application']:
                    PlanRoleApp.objects.create(plan_role=obj, application_id=app_id)

        if len(ids_valid) < len(plan_app_data_dict.keys()):
            for plan_id, data in plan_app_data_dict.items():
                if plan_id not in ids_valid:
                    obj = PlanRole.objects.create(plan_id=plan_id, role=self, application=data['application'])
                    for app_id in data['application']:
                        PlanRoleApp.objects.create(plan_role=obj, application_id=app_id)
        return super().save()

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RoleHolder(SimpleAbstractModel):
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


class PlanRole(SimpleAbstractModel):
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE,
        related_name='role_plans',
    )
    role = models.ForeignKey(
        'hr.Role',
        on_delete=models.CASCADE,
        related_name='role_plan_app',
    )
    application = models.JSONField(default=list)
    application_m2m = models.ManyToManyField(
        'base.Application',
        through='PlanRoleApp',
        related_name='role_apps',
        symmetrical=False,
        blank=True,
    )

    class Meta:
        verbose_name = 'Plan of Role'
        verbose_name_plural = 'Plan of Role'
        default_permissions = ()
        permissions = ()


class PlanRoleApp(SimpleAbstractModel):
    plan_role = models.ForeignKey(
        'hr.PlanRole',
        on_delete=models.CASCADE,
        related_name='app_of_plan_role',
    )
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        related_name='app_use_by_plan_role',
    )

    class Meta:
        verbose_name = 'App of Plan Role'
        verbose_name_plural = 'App of Plan Role'
        unique_together = ('plan_role', 'application')
        default_permissions = ()
        permissions = ()


# Group Level
class GroupLevel(TenantAbstractModel):
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


# group | department
class Group(TenantAbstractModel):
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
    group_employee = models.JSONField(
        verbose_name="group employee",
        null=True,
        default=list
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
        return [str(x) for x in cls.objects.filter(first_manager_id=employee_id).values_list('id', flat=True)]
