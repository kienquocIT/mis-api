from django.contrib.auth.models import Permission
from django.db import models
from jsonfield import JSONField

from apps.shared import TenantCoreModel, M2MModel, GENDER_CHOICE


class Employee(TenantCoreModel):
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
        'tenant.Space',
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

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # setup full name for search engine
        self.search_content = f'{self.first_name} {self.last_name} , {self.last_name} {self.first_name} , {self.code}'
        super(Employee, self).save(*args, **kwargs)

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


class SpaceEmployee(M2MModel):
    space = models.ForeignKey('tenant.Space', on_delete=models.CASCADE)
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
        'tenant.SubscriptionPlan',
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


class Role(TenantCoreModel):
    abbreviation = models.CharField(
        verbose_name='abbreviation of role (Business analysis -> BA)',
        max_length=10,
        blank=True,
        null=True
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
class Group(TenantCoreModel):
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


# M2M Group Employee
class GroupEmployee(M2MModel):
    group = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name="group_employee_group",
        null=True
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="group_employee_employee",
        null=True
    )
    role = JSONField(
        verbose_name="role",
        null=True,
        default=[]
    )
