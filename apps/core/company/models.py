import json
from typing import Literal, Union
from uuid import UUID
from jsonfield import JSONField
from django.db import models
from django.conf import settings
from apps.shared import SimpleAbstractModel, MasterDataAbstractModel, CURRENCY_MASK_MONEY, MediaForceAPI
from apps.core.models import CoreAbstractModel
from django.utils.translation import gettext_lazy as _


DEFINITION_INVENTORY_VALUATION_CHOICES = [
    (0, _('Perpetual inventory')),
    (1, _('Periodic inventory')),
]

DEFAULT_INVENTORY_VALUE_METHOD_CHOICES = [
    (0, _('FIFO')),
    (1, _('Cumulative weighted average')),
    (2, _('Weighted average')),
    (3, _('Specific identification method')),
]

NUMBERING_BY_CHOICES = [
    (0, _('System')),
    (1, _('User defined')),
]

RESET_FREQUENCY_CHOICES = [
    (0, _('Yearly')),
    (1, _('Monthly')),
    (2, _('Weekly')),
    (3, _('Daily')),
    (4, _('Never')),
]

FUNCTION_CHOICES = [
    (0, _('Opportunity')),
    (1, _('Sale quotation')),
    (2, _('Sale order')),
    (3, _('Picking')),
    (4, _('Delivery')),
    (5, _('Task')),
    (6, _('Advance payment')),
    (7, _('Payment')),
    (8, _('Return payment')),
    (9, _('Purchase request')),
]


class Company(CoreAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)
    code = models.CharField(max_length=25, blank=True)

    # license used
    # {
    #       '{code_Plan}': 99,
    # }
    license_usage = models.JSONField(default=dict)

    # Total | receive from client, increase or decrease
    total_user = models.IntegerField(default=0)
    representative_fullname = models.CharField(
        verbose_name='fullname',
        max_length=100,
        blank=True,
    )
    address = models.CharField(
        verbose_name='address',
        blank=True,
        null=True,
        max_length=150
    )
    email = models.CharField(
        verbose_name='email',
        blank=True,
        null=True,
        max_length=150
    )
    phone = models.CharField(
        verbose_name='phone',
        blank=True,
        null=True,
        max_length=25
    )
    fax = models.CharField(
        verbose_name='fax',
        blank=True,
        null=True,
        max_length=25
    )

    # media
    media_company_id = models.UUIDField(null=True)
    media_company_code = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @property
    def config(self) -> Union[None, models.Model]:
        try:
            return CompanyConfig.objects.get(company=self)
        except CompanyConfig.DoesNotExist:
            pass
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update total company of tenant
        if self.tenant:
            self.tenant.company_total = self.__class__.objects.filter(tenant=self.tenant).count()
            self.tenant.save()
        else:
            print(f'[Company|Save] Tenant does not exist {self.tenant}')

        if kwargs.get('force_insert', False) and not self.media_company_id and settings.ENABLE_PROD is True:
            MediaForceAPI.call_sync_company(self)

    @classmethod
    def refresh_total_user(cls, ids):
        for obj in cls.objects.filter(id__in=ids):
            obj.total_user = CompanyUserEmployee.objects.filter(company_id=obj.id, user__isnull=False).count()
            obj.save(update_fields=['total_user'])
        return True


class CompanyConfig(SimpleAbstractModel):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGE_CHOICE,
        default='vi',
        verbose_name='Default language of Company',
        help_text='Using language for company create in company',
    )
    currency = models.ForeignKey(
        'base.Currency',
        on_delete=models.CASCADE,
        verbose_name='Currency was used by Company',
    )
    currency_rule = models.JSONField(
        default=dict,
        verbose_name='Config display currency',
        help_text=json.dumps(
            {
                'prefix': '',
                'suffix': ' VND',
                'affixesStay': True,
                'thousands': '.',
                'decimal': ',',
                'precision': 0,
                'allowZero': True,
                'allowNegative': False,
            }
        )
    )

    class Meta:
        verbose_name = 'Currency was used by Company'
        verbose_name_plural = 'Currency was used by Company'
        default_permissions = ()
        permissions = ()

    def before_save(self, **kwargs):
        self.language = self.language.lower()
        if kwargs.get('force_insert', False):
            if self.currency:
                if self.currency.code.upper() in CURRENCY_MASK_MONEY:
                    self.currency_rule = CURRENCY_MASK_MONEY[self.currency.code.upper()]
                else:
                    self.currency_rule = CURRENCY_MASK_MONEY['USD']
                    self.currency_rule['prefix'] = f'{self.currency.code} '
        return True

    def save(self, *args, **kwargs):
        self.before_save(**kwargs)
        super().save(*args, **kwargs)


class CompanyLicenseTracking(SimpleAbstractModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # User
    user = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True)
    user_info = JSONField(default={})

    # code plan used
    license_plan = models.CharField(max_length=50)

    # sum license was used of company
    license_use_count = models.IntegerField()

    # some log, maybe it is user info just created
    log_msg = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Company License Tracking'
        verbose_name_plural = 'Company License Tracking'
        default_permissions = ()
        permissions = ()


class CompanyUserEmployee(SimpleAbstractModel):
    """
    Case 1: Tao moi user (employee=null) --> Create new
    Case 2: Tap moi employee:
        Case 2.1: user=null --> Create new
        Case 2.2: user co data --> Goi toi case 3
    Case 3: Cap nhat user vao employee
        Step 1: Tim 2 Map Obj | Emp Map co user=null | User Map co employee=null
        Step 2: Xoa Employee Map
        Step 3: Cap nhat User Map employee=employee va luu lai
    Case 4: Xoa user khoi employee
        Step 1: Tim Map Obj co user=user + employee=employee
        Step 2: Cap nhat Map Obj employee=null
        Step 3: Goi case 2
    Case 5: Chuyen user khac vao employee
        Step 1: Goi case 4 voi user cu
        Step 2: Goi Case 3 voi user moi
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        related_name='company_user_employee_set_user',
        null=True
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        related_name='company_user_employee_set_employee',
        null=True
    )
    is_created_company = models.BooleanField(verbose_name='company user created', default=False)

    class Meta:
        verbose_name = 'Company Map Employee Map User'
        verbose_name_plural = 'Company Map Employee Map User'
        unique_together = ('company', 'user', 'employee')
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_obj_map(cls, objs, is_user_or_employee: Literal['user', 'employee']):
        if objs.count() == 1:
            obj_map = objs.first()
            if is_user_or_employee == 'user':
                if obj_map.employee_id is None:
                    return obj_map
                return None
            if is_user_or_employee == 'employee':
                if obj_map.user_id is None:
                    return obj_map
                return None
            raise AttributeError(
                f'[CompanyUserEmployee.check_obj_map] '
                f'check_user_or_employee not support code: {is_user_or_employee}'
            )
        raise RuntimeError(
            '[CompanyUserEmployee.create_new] User Map return more than one records.'
        )

    @classmethod
    def create_new(
            cls, company_id, employee_id=None, user_id=None, is_created_company=True
    ) -> models.Model or Exception:
        # must be employee_id and user_id : one arg have data, remaining arg is None
        if company_id:
            if (employee_id and user_id) or (not employee_id and not user_id):
                raise AttributeError(
                    '[CompanyUserEmployee.create_new] Employee ID or User ID must be required. '
                    'Remaining argument must be is None'
                )
            if employee_id:
                emp_map = cls.objects.filter(company_id=company_id, employee_id=employee_id)
                if emp_map:
                    return cls.check_obj_map(emp_map, 'employee')
                return cls.objects.create(
                    company_id=company_id, employee_id=employee_id, user_id=None
                )
            if user_id:
                user_map = cls.objects.filter(company_id=company_id, user_id=user_id)
                if user_map:
                    return cls.check_obj_map(user_map, 'user')
                return cls.objects.create(
                    company_id=company_id, employee_id=None, user_id=user_id,
                    is_created_company=is_created_company,
                )
        raise AttributeError('[CompanyUserEmployee.create_new] Company ID must be required.')

    @classmethod
    def remove_map(cls, company_id, employee_id, user_id) -> (models.Model, models.Model) or Exception:
        if company_id and employee_id and user_id:
            objs = cls.objects.filter(company_id=company_id, employee_id=employee_id, user_id=user_id)
            if objs.count() <= 1:
                obj_user = objs.first()
                if obj_user:
                    obj_user.employee_id = None
                    obj_user.save()
                    obj_employee = cls.create_new(company_id, employee_id, user_id=None)
                    return obj_user, obj_employee
                raise RuntimeError('[CompanyUserEmployee.remove_map] Find Obj Map returned null.')
            raise RuntimeError('[CompanyUserEmployee.remove_map] Get Map Obj returned two records.')
        raise AttributeError(
            '[CompanyUserEmployee.remove_map] Company ID, Employee ID, User ID must be required.'
        )

    @classmethod
    def assign_map(cls, company_id, employee_id, user_id):
        if company_id and employee_id and user_id:
            user_map = cls.objects.filter(company_id=company_id, user_id=user_id)
            emp_map = cls.objects.filter(company_id=company_id, employee_id=employee_id)
            if user_map and emp_map:
                user_map = cls.check_obj_map(user_map, 'user')
                emp_map = cls.check_obj_map(emp_map, 'employee')
                if (
                        user_map and isinstance(user_map, models.Model)
                        and emp_map and isinstance(emp_map, models.Model)
                ):
                    emp_map.delete()
                    user_map.employee_id = employee_id
                    user_map.save()
                    return True
                raise user_map
        raise RuntimeError(
            '[CompanyUserEmployee.assign_map] Data argument check is incorrect so assign returned failure.'
        )

    @classmethod
    def remove_company_from_user(cls, user_id, company_ids):
        for obj in cls.objects.filter(company_id__in=company_ids, user_id=user_id):
            if obj.employee_id:
                employee_id = obj.employee_id
                obj.employee.user = None
                obj.employee.save(update_fields=['user'])
                obj.delete()
                cls.create_new(obj.company_id, employee_id, user_id=None, is_created_company=False)
            else:
                obj.delete()
        return True

    @classmethod
    def add_company_to_user(cls, user_id, company_ids):
        for _id in company_ids:
            if not cls.objects.filter(company_id=_id, user_id=user_id).exists():
                cls.create_new(_id, None, user_id=user_id, is_created_company=False)
        return True

    @classmethod
    def all_user_of_company(cls, company_id: Union[UUID, str]):
        return list(
            set(
                cls.objects.filter(company_id=company_id).values_list('user_id', flat=True).cache()
            )
        )


class CompanySetting(SimpleAbstractModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_setting')
    primary_currency = models.ForeignKey('base.Currency', on_delete=models.CASCADE, null=True)
    definition_inventory_valuation = models.SmallIntegerField(choices=DEFINITION_INVENTORY_VALUATION_CHOICES, default=0)
    default_inventory_value_method = models.SmallIntegerField(choices=DEFAULT_INVENTORY_VALUE_METHOD_CHOICES, default=0)
    cost_per_warehouse = models.BooleanField(default=False)
    cost_per_lot_batch = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Company Setting'
        verbose_name_plural = 'Company Settings'
        ordering = ()
        default_permissions = ()
        permissions = ()


class CompanyFunctionNumber(MasterDataAbstractModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_function_number')
    function = models.SmallIntegerField(choices=FUNCTION_CHOICES)
    numbering_by = models.SmallIntegerField(choices=NUMBERING_BY_CHOICES, default=0)
    schema = models.CharField(max_length=500, null=True)
    schema_text = models.CharField(max_length=500, null=True)
    first_number = models.IntegerField(null=True)
    last_number = models.IntegerField(null=True)
    reset_frequency = models.SmallIntegerField(choices=RESET_FREQUENCY_CHOICES, null=True)

    class Meta:
        verbose_name = 'Company Function Number'
        verbose_name_plural = 'Company Functions Number'
        ordering = ()
        default_permissions = ()
        permissions = ()
