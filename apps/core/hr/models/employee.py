from django.db import models

from apps.core.attachments.storages.aws.storages_backend import PublicMediaStorage
from apps.core.hr.models.private_extends import PermissionAbstractModel
from apps.core.models import TenantAbstractModel
from apps.shared import SimpleAbstractModel, GENDER_CHOICE, StringHandler, TypeCheck, DisperseModel

__all__ = [
    'Employee',
    'SpaceEmployee',
    'EmployeePermission',
    'PlanEmployee',
    'PlanEmployeeApp',
]


def generate_employee_avatar_path(instance, filename):
    def get_ext():
        return filename.split(".")[-1].lower()

    if instance.id:
        company_path = str(instance.company_id).replace('-', '')
        employee_id = str(instance.id).replace('-', '')
        return f"{company_path}/global/avatar/{employee_id}.{get_ext()}"
    raise ValueError('Attachment require employee related')


class Employee(TenantAbstractModel):
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

    # as sum data permissions
    permissions_parsed_sample = {
        'hr.employee.view': {
            '4': {},
            'ids': {
                '{doc_id}': {},
            },
            'opp': {
                '{opp_id}': {
                    'me': {},
                    'all': {},
                },
            },
            'prj': {
                '{project_id}': {
                    'me': {},
                    'all': {},
                },
            },
        },
        'hr.employee.edit': {'4': {}},
        '{app_label}.{model_code}.{perm_code}': {'{range_code}': {}},
    }
    permissions_parsed = models.JSONField(default=dict, verbose_name='Data was parsed')

    #
    avatar_img = models.ImageField(
        storage=PublicMediaStorage, upload_to=generate_employee_avatar_path, null=True,
    )

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee'
        ordering = ('-date_created',)
        unique_together = ('company', 'code', 'is_delete')
        default_permissions = ()
        permissions = ()

    def __repr__(self):
        return self.first_name + '. ' + self.last_name

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

    def append_permit_by_ids(self, app_label, model_code, perm_code, doc_id, tenant_id):
        employee_permit_obj, _created = EmployeePermission.objects.get_or_create(employee=self)
        return employee_permit_obj.append_permit_by_ids(
            app_label=app_label, model_code=model_code, perm_code=perm_code, doc_id=doc_id, tenant_id=tenant_id
        )

    @classmethod
    def generate_code(cls, company_id):
        num_max = None
        for item in cls.objects.filter(company_id=company_id).values_list('code', flat=True):
            try:
                tmp = int(str(item).split('-', maxsplit=1)[0].split("EMP")[1])
                if not num_max or (isinstance(num_max, int) and tmp > num_max):
                    num_max = tmp
            except Exception as err:
                print(err)

        if num_max:
            if num_max < 10000:
                if num_max > 1000:
                    code = 'EMP' + str(num_max + 1)
                elif num_max > 100:
                    code = 'EMP0' + str(num_max + 1)
                elif num_max > 10:
                    code = 'EMP00' + str(num_max + 1)
                else:
                    code = 'EMP000' + str(num_max + 1)
            else:
                raise ValueError('Out range 10000 employee number')
        else:
            code = 'EMP0001-' + StringHandler.random_str(17)

        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    def save(self, *args, **kwargs):
        # setup full name for search engine
        self.search_content = f'{self.first_name} {self.last_name} , {self.last_name} {self.first_name} , {self.code}'

        # auto create code (temporary)

        # get old user and new user
        user_id_old, user_id_new = None, self.user_id
        if not kwargs.get('force_insert', False):
            user_id_old, user_id_new = self.check_change_user()

        # hit DB
        super().save(*args, **kwargs)

        # call sync
        self.sync_company_map(user_id_old, user_id_new, is_new=kwargs.get('force_insert', False))

    def get_detail_minimal(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'avatar_img': self.avatar_img.url if self.avatar_img else None,
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
            'avatar_img': self.avatar_img.url if self.avatar_img else None,
            'group': self.group_id,
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

    def permit_obj(self):
        obj, _created = EmployeePermission.objects.get_or_create(employee=self)
        return obj

    def permit_obj__permission_by_configured(self) -> list:
        obj, _created = EmployeePermission.objects.get_or_create(employee=self)
        return obj.permission_by_configured


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
    plan = models.ForeignKey('base.SubscriptionPlan', on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)
    application = models.JSONField(default=list)
    application_m2m = models.ManyToManyField(
        'base.Application',
        through='PlanEmployeeApp',
        related_name='employee_apps',
        symmetrical=False,
        blank=True,
    )

    class Meta:
        verbose_name = 'Plan of Employee'
        verbose_name_plural = 'Plan of Employee'
        default_permissions = ()
        permissions = ()
        ordering = ('plan__title',)


class PlanEmployeeApp(SimpleAbstractModel):
    plan_employee = models.ForeignKey('hr.PlanEmployee', on_delete=models.CASCADE, related_name='app_of_plan_employee')
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        related_name='app_use_by_plan_employee',
    )

    class Meta:
        verbose_name = 'App of Plan Role'
        verbose_name_plural = 'App of Plan Role'
        unique_together = ('plan_employee', 'application')
        default_permissions = ()
        permissions = ()
        ordering = ('application__title',)


class EmployeePermission(SimpleAbstractModel, PermissionAbstractModel):
    employee = models.OneToOneField('hr.Employee', on_delete=models.CASCADE)

    def get_app_allowed(self) -> str:
        return str(self.employee_id)

    def sync_parsed_to_main(self):
        self.employee.permissions_parsed = self.permissions_parsed
        self.employee.save(update_fields=['permissions_parsed'])

    def save(self, *args, **kwargs):
        sync_parsed = kwargs.pop('sync_parsed', False)
        super().save(*args, **kwargs)
        if sync_parsed is True:
            self.sync_parsed_to_main()

    class Meta:
        verbose_name = 'Permission of Employee'
        verbose_name_plural = 'Permission of Employee'
        default_permissions = ()
        permissions = ()
