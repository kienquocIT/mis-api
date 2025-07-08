import re
import json
import datetime
import calendar
from typing import Literal, Union
from uuid import UUID

from jsonfield import JSONField
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.core.attachments.storages.aws.storages_backend import PublicMediaStorage
from apps.shared import SimpleAbstractModel, CURRENCY_MASK_MONEY
from apps.core.models import CoreAbstractModel

DEFINITION_INVENTORY_VALUATION_CHOICES = [
    (0, _('Perpetual inventory')),
    (1, _('Periodic inventory')),
]

DEFAULT_INVENTORY_VALUE_METHOD_CHOICES = [
    (0, _('FIFO')),
    (1, _('Weighted average')),
    (2, _('Specific identification method')),
]

ACCOUNTING_POLICIES_CHOICES = [
    (0, _('VAS')),
    (1, _('IAS')),
]

APPLICABLE_CIRCULAR_CHOICES = [
    (0, '200/2014/TT-BTC'),
    (1, '133/2015/TT-BTC'),
]

RESET_FREQUENCY_CHOICES = [
    (0, _('Yearly')),
    (1, _('Monthly')),
    (2, _('Weekly')),
    (3, _('Daily')),
    (4, _('Never')),
]


def generate_company_logo_path(instance, filename):  # pylint: disable=W0613
    if instance.id:
        company_path = str(instance.id).replace('-', '')
        return f"{company_path}/global/logo.png"
    raise ValueError('Attachment require company related')


def generate_company_icon_path(instance, filename):  # pylint: disable=W0613
    if instance.id:
        company_path = str(instance.id).replace('-', '')
        return f"{company_path}/global/logo.ico"
    raise ValueError('Attachment require company related')


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
    software_start_using_time = models.DateTimeField(null=True)
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

    # web builder | tenant_code : 10 + company_code : 25 = 35
    sub_domain = models.CharField(max_length=35, unique=True)

    #
    logo = models.ImageField(storage=PublicMediaStorage, upload_to=generate_company_logo_path, null=True)
    icon = models.ImageField(storage=PublicMediaStorage, upload_to=generate_company_icon_path, null=True)

    # config data
    function_number_data = models.JSONField(default=list)
    # {'app_type',
    # 'app_code',
    # 'app_title',
    # 'schema_text',
    # 'schema',
    # 'first_number',
    # 'last_number',
    # 'reset_frequency',
    # 'min_number_char'}

    def get_detail(self, excludes=None):
        return {
            'id': str(self.id),
            'title': str(self.title) if self.title else None,
            'code': str(self.code) if self.code else None,
            'sub_domain': self.sub_domain,
            'logo': self.logo.url if self.logo else None,
            'icon': self.icon.url if self.icon else None,
        }

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'code',)

    @property
    def config(self) -> Union[None, models.Model]:
        try:
            return CompanyConfig.objects.get(company=self)
        except CompanyConfig.DoesNotExist:
            pass
        return None

    def make_sub_domain_unique(self, counter=0):
        gen_sub_domain = f'{self.code}{"" if counter == 0 else str(counter)}'.lower()
        if not self.__class__.objects.filter(sub_domain=gen_sub_domain).exists():
            return gen_sub_domain
        return self.make_sub_domain_unique(counter=counter+1)

    def save(self, *args, **kwargs):
        if not self.sub_domain:
            gen_sub_domain = self.make_sub_domain_unique(counter=0)
            self.sub_domain = gen_sub_domain
        self.code = self.code.lower()
        self.sub_domain = self.sub_domain.lower()
        super().save(*args, **kwargs)

    @classmethod
    def refresh_total_user(cls, ids):
        for obj in cls.objects.filter(id__in=ids):
            obj.total_user = CompanyUserEmployee.objects.filter(company_id=obj.id, user__isnull=False).count()
            obj.save(update_fields=['total_user'])
        return True


class CompanyConfig(SimpleAbstractModel):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='company_config')
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
        null=True,
        verbose_name='Base currency was used by Company',
    )
    master_data_currency = models.ForeignKey(
        'saledata.Currency',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Master data currency',
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
    definition_inventory_valuation = models.SmallIntegerField(choices=DEFINITION_INVENTORY_VALUATION_CHOICES, default=0)
    default_inventory_value_method = models.SmallIntegerField(choices=DEFAULT_INVENTORY_VALUE_METHOD_CHOICES, default=1)
    cost_per_warehouse = models.BooleanField(default=True)
    cost_per_lot = models.BooleanField(default=False)
    cost_per_project = models.BooleanField(default=False)
    accounting_policies = models.SmallIntegerField(choices=ACCOUNTING_POLICIES_CHOICES, default=0)
    applicable_circular = models.SmallIntegerField(choices=APPLICABLE_CIRCULAR_CHOICES, default=0)

    class Meta:
        verbose_name = 'Company Config'
        verbose_name_plural = 'Company Config'
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
    def confirm_dif_obj_map(cls, objs_1, objs_2) -> bool | None:
        if objs_1.count() == 1 and objs_2.count() == 1:
            if objs_1.first() == objs_2.first():
                return True
            return None
        return False

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
                state_confirm = cls.confirm_dif_obj_map(user_map, emp_map)
                if isinstance(state_confirm, bool):
                    return state_confirm
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
                raise RuntimeError(
                    '[CompanyUserEmployee.assign_map] user_map and emp_map not only or not exist for merge.'
                )
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
                cls.objects.filter(company_id=company_id).values_list('user_id', flat=True)
            )
        )


class CompanyFunctionNumber(SimpleAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_function_number')
    app_type = models.SmallIntegerField(choices=[(0, _('Application')), (1, _('Master data'))], default=0)
    app_code = models.CharField(max_length=150, blank=True, null=True, help_text='App code')
    app_title = models.CharField(max_length=150, blank=True, null=True, help_text='App title')
    schema = models.CharField(max_length=500, null=True)
    schema_text = models.CharField(max_length=500, null=True)
    first_number = models.IntegerField(null=True, blank=True)
    last_number = models.IntegerField(null=True, blank=True)
    reset_frequency = models.SmallIntegerField(choices=RESET_FREQUENCY_CHOICES, null=True)
    min_number_char = models.IntegerField(null=True, blank=True)
    latest_number = models.IntegerField(null=True, blank=True)
    year_reset = models.IntegerField(null=True, blank=True)
    month_reset = models.IntegerField(null=True, blank=True)
    week_reset = models.IntegerField(null=True, blank=True)
    day_reset = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Company Function Number'
        verbose_name_plural = 'Company Functions Number'
        ordering = ()
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_reset_field_name(cls, reset_frequency):
        reset_frequency_fields = ['year_reset', 'month_reset', 'week_reset', 'day_reset']
        if reset_frequency < len(reset_frequency_fields):
            return reset_frequency_fields[reset_frequency]
        raise RuntimeError('[CompanyFunctionNumber.reset_frequency] Find Field Map returned null.')

    @classmethod
    def parse_code_from_schema(cls, obj, schema):
        # check_reset_frequency
        parsed_code = ''
        current_year, current_month = datetime.datetime.now().year, datetime.datetime.now().month
        data_calendar = datetime.date.today().isocalendar()
        new_latest_number = obj.latest_number
        is_reset = None
        reset_type = None
        conditions = [
            (0, obj.year_reset, current_year),
            (1, obj.month_reset, f"{current_year}{current_month:02}"),
            (2, obj.week_reset, f"{data_calendar[0]}{data_calendar[1]:02}"),
            (3, obj.day_reset, f"{data_calendar[0]}{data_calendar[1]:02}{data_calendar[2]}")
        ]
        for reset_frequency, reset_value, new_value in conditions:
            if obj.reset_frequency == reset_frequency and reset_value < int(new_value):
                setattr(obj, f"{obj.get_reset_field_name(reset_frequency)}", int(new_value))
                is_reset = new_value
                reset_type = reset_frequency
                break
        if is_reset:
            new_latest_number = obj.first_number - 1

        new_latest_number = new_latest_number + 1

        schema_item_list = [
            str(new_latest_number).zfill(obj.min_number_char) if obj.min_number_char else str(new_latest_number),
            str(current_year % 100),
            str(current_year),
            str(calendar.month_name[current_month][0:3]),
            str(calendar.month_name[current_month]),
            str(current_month).zfill(2),
            str(data_calendar[1]).zfill(2),
            str(datetime.date.today().timetuple().tm_yday).zfill(3),
            str(datetime.date.today().day).zfill(2),
            str(data_calendar[2])
        ]
        for match in re.findall(r"\[.*?\]", schema):
            parsed_code = schema.replace(match, str(schema_item_list[int(match[1:-1])]))

        if obj.app_type == 0:
            if reset_type == 0:
                obj.year_reset = is_reset
            if reset_type == 1:
                obj.month_reset = is_reset
            if reset_type == 2:
                obj.week_reset = is_reset
            if reset_type == 3:
                obj.day_reset = is_reset
            obj.latest_number = new_latest_number
            obj.save(update_fields=['year_reset', 'month_reset', 'week_reset', 'day_reset', 'latest_number'])

        return parsed_code

    @classmethod
    def auto_gen_code_based_on_config(cls, app_code=None, in_workflow=True, instance=None, kwargs=None):
        code_rules = {
            'advancepayment': 'AP[n4]',
            'arinvoice': 'AR[n4]',
            'bidding': 'BD[n4]',
            'bom': 'BOM[n4]',
            'cashinflow': 'CIF[n4]',
            'cashoutflow': 'COF[n4]',
            'distributionplan': 'DP[n4]',
            'equipmentloan': 'EL-[n4]',
            'equipmentreturn': 'ER-[n4]',
            'fixedasset': 'FA[n4]',
            'fixedassetwriteoff': 'FAW[n4]',
            'goodsissue': 'GI[n4]',
            'goodsreceipt': 'GR[n4]',
            'goodsrecovery': 'GRC[n4]',
            'goodsreturn': 'GRT[n4]',
            'goodstransfer': 'GT[n4]',
            'instrumenttool': 'IT[n4]',
            'instrumenttoolwriteoff': 'ITW[n4]',
            'inventoryadjustment': 'IA[n4]',
            'kmsdocumentapproval': 'KDA[n4]',
            'kmsincomingdocument': 'ID[n4]',
            'lead': 'LEAD[n4]',
            'opportunity': 'OPP[n4]',
            'orderdeliverysub': 'DE[n4]',
            'payment': 'PM[n4]',
            'productmodification': 'PRD-MOD-[n4]',
            'purchaserequest': 'PR[n4]',
            'reconciliation': 'RECON[n4]',
            'returnadvance': 'RP[n4]'
        }

        parsed_code = ''

        # tạo auto trước
        if instance and app_code in code_rules:
            parsed_code = instance.auto_generate_code(instance, code_rules[app_code], in_workflow)

        # kiểm tra nếu có cấu hình người dùng thì gen mới
        obj = cls.objects.filter_on_company(app_code=app_code).first()
        if obj and obj.schema is not None:
            parsed_code = cls.parse_code_from_schema(obj, obj.schema)

        if instance:
            instance.code = parsed_code
            if in_workflow and kwargs:
                kwargs['update_fields'].append('code')

        return parsed_code

    @classmethod
    def auto_code_update_latest_number(cls, app_code):
        obj = cls.objects.filter_on_company(app_code=app_code).first()
        if obj:
            obj.latest_number = obj.latest_number + 1
            obj.save(update_fields=['latest_number'])
        return True
