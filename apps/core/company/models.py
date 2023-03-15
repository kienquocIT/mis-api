from typing import Literal
from jsonfield import JSONField
from django.db import models

from apps.shared import SimpleAbstractModel

from apps.core.models import CoreAbstractModel


class Company(CoreAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)

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

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update total company of tenant
        if self.tenant:
            self.tenant.company_total = self.__class__.objects.filter(tenant=self.tenant).count()
            self.tenant.save()
        else:
            print(f'[Company|Save] Tenant does not exist {self.tenant}')


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
    user = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True)
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
    def create_new(cls, company_id, employee_id=None, user_id=None) -> models.Model or Exception:
        # must be employee_id and user_id : one arg have data, remaining arg is None
        if company_id:
            if (employee_id and user_id) or (not employee_id and not user_id):
                raise AttributeError(
                    '[CompanyUserEmployee.create_new] Employee ID or User ID must be required. '
                    'Remaining argument must be is None'
                )
            if employee_id:
                emp_map = cls.object_normal.filter(company_id=company_id, employee_id=employee_id)
                if emp_map:
                    return cls.check_obj_map(emp_map, 'employee')
                return cls.object_normal.create(
                    company_id=company_id, employee_id=employee_id, user_id=None
                )
            if user_id:
                user_map = cls.object_normal.filter(company_id=company_id, user_id=user_id)
                if user_map:
                    return cls.check_obj_map(user_map, 'user')
                return cls.object_normal.create(
                    company_id=company_id, employee_id=None, user_id=user_id,
                    is_created_company=True,
                )
        raise AttributeError('[CompanyUserEmployee.create_new] Company ID must be required.')

    @classmethod
    def remove_map(cls, company_id, employee_id, user_id) -> (models.Model, models.Model) or Exception:
        if company_id and employee_id and user_id:
            objs = cls.object_normal.filter(company_id=company_id, employee_id=employee_id, user_id=user_id)
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
            user_map = cls.object_normal.filter(company_id=company_id, user_id=user_id)
            emp_map = cls.object_normal.filter(company_id=company_id, employee_id=employee_id)
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
