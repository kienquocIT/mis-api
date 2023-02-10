import datetime
import json

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from apps.shared import ProvisioningMsg

from apps.core.tenant.models import Tenant, TenantPlan
from apps.core.base.models import SubscriptionPlan

from .serializers import (
    TenantCreateSerializer, CompanyCreateSerializer, SpaceCreateSerializer, EmployeeCreateSerializer,
    UserCreateSerializer, EmployeeSpaceCreateSerializer
)
from ..company.models import CompanyUserEmployee


class TenantController:
    """
    NEW TENANT:
    Step
    1. create tenant
    2. create company
    3. create space
    4. create employee
    5. create account (map: tenant, company, space.first, employee)
    6. update employee (map: user by account)
    7. create employee-space
    """

    def __init__(self):
        self.tenant_obj = None
        self.company_obj = None
        self.space_obj = None
        self.employee_obj = None
        self.user_obj = None

    def setup_new(
            self,
            tenant_code,
            tenant_data: dict,
            user_data: dict,
            create_company: bool,
            create_employee: bool,
            plan_data,
    ) -> serializers.ValidationError or bool:
        try:
            with transaction.atomic():
                plan_obj_list = self.check_and_create_plan(plan_data)
                self.tenant_obj = self.get_tenant_by_code(tenant_code)
                if not self.tenant_obj:
                    tenant_data.update({'code': tenant_code})
                    tenant_data.update({'plan': json.dumps(plan_data)})
                    self.tenant_obj = self.create_tenant(
                        **tenant_data,
                    )

                    # create TenantPlan
                    if plan_obj_list and self.tenant_obj:
                        self.create_tenant_plan(
                            plan_obj_list=plan_obj_list,
                            tenant_obj=self.tenant_obj
                        )

                    # create Company
                    self.company_obj, self.space_obj = None, None
                    if create_company is True:
                        self.company_obj = self.create_company(
                            title=self.tenant_obj.title,
                            code=f'{self.tenant_obj.code}01',
                            tenant=self.tenant_obj.id,
                            total_user=1,
                        )
                        self.space_obj = self.create_space(
                            title='Global',
                            code=f'{tenant_code.upper()} Global',
                            tenant=self.tenant_obj.id,
                            company=self.company_obj.id,
                            is_system=True,
                        )

                    # create employee & create User
                    if self.tenant_obj and user_data:
                        # create user
                        self.setup_user(user_data)
                        # create map user - company
                        self.user_obj.sync_map(self.company_obj.id)
                        # create employee
                        if create_employee and self.company_obj:
                            self.employee_obj = self.create_employee(
                                first_name=self.user_obj.first_name,
                                last_name=self.user_obj.last_name,
                                phone=self.user_obj.phone,
                                email=self.user_obj.email,
                                tenant=self.tenant_obj.id,
                                company=self.company_obj.id,
                                user=self.user_obj.id
                            )
                            # self.update_employee(self.employee_obj, user=self.user_obj)
                            self.update_user(self.user_obj, employee_current=self.employee_obj)
                            if self.space_obj:
                                self.create_space_employee(self.employee_obj, self.space_obj, **{})

                    return True
                raise serializers.ValidationError({
                    'detail': ProvisioningMsg.TENANT_READY.format(tenant_code),
                    'step': 'Check tenant ready'
                })
        except serializers.ValidationError as err:
            raise err
        except Exception as err:
            raise serializers.ValidationError({'detail': f'Setup new tenant failure with code: [{str(err)}]'})
        return False

    def setup_user(self, user_data):
        self.user_obj = self.create_user(
            username_auth=get_user_model().convert_username_field_data(
                user_data['username'], self.tenant_obj
            ),
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            email=user_data['email'],
            is_admin_tenant=True,
            tenant_current=self.tenant_obj.id,
            company_current=self.company_obj.id if self.company_obj else None,
            space_current=self.space_obj.id if self.space_obj else None,
            employee_current=None,
        )
        if self.user_obj.is_admin_tenant:
            self.update_tenant(
                self.tenant_obj,
                admin_info={
                    'fullname': f'{self.user_obj.first_name} {self.user_obj.last_name}',
                    'phone_number': str(self.user_obj.phone),
                    'username': str(self.user_obj.username),
                    'email': str(self.user_obj.email),
                },
                admin_created=True,
                admin=self.user_obj
            )
        return self.user_obj

    @classmethod
    def get_tenant_by_code(cls, tenant_code):
        obj = Tenant.objects.filter(code=tenant_code).first()
        return obj if obj else None

    @classmethod
    def create_tenant(cls, **kwargs):
        try:
            ser = TenantCreateSerializer(data=kwargs)
            ser.is_valid(raise_exception=True)
            return ser.save()
        except serializers.ValidationError as err:
            err.detail['step'] = [ErrorDetail(string='In step setup tenant')]
            raise err
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step setup tenant',
                'detail': str(err),
            })

    @classmethod
    def update_tenant(cls, obj, **kwargs):
        # update flag admin_created, admin obj
        # admin_created, admin
        try:
            obj.refresh_from_db()
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step update tenant',
                'detail': str(err),
            })
        return obj

    @classmethod
    def create_company(cls, **kwargs):
        try:
            ser = CompanyCreateSerializer(data=kwargs)
            ser.is_valid(raise_exception=True)
            return ser.save()
        except serializers.ValidationError as err:
            err.detail['step'] = [ErrorDetail(string='In step setup company')]
            raise err
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step setup company',
                'detail': str(err),
            })

    @classmethod
    def create_space(cls, **kwargs):
        try:
            ser = SpaceCreateSerializer(data=kwargs)
            ser.is_valid(raise_exception=True)
            return ser.save()
        except serializers.ValidationError as err:
            err.detail['step'] = [ErrorDetail(string='In step setup space')]
            raise err
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step setup space',
                'detail': str(err),
            })

    @classmethod
    def create_employee(cls, **kwargs):
        try:
            ser = EmployeeCreateSerializer(data=kwargs)
            ser.is_valid(raise_exception=True)
            return ser.save(
                tenant_id=kwargs.get('tenant'),
                company_id=kwargs.get('company')
            )
        except serializers.ValidationError as err:
            err.detail['step'] = [ErrorDetail(string='In step setup employee')]
            raise err
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step setup employee',
                'detail': str(err),
            })

    @classmethod
    def update_employee(cls, obj, **kwargs):
        # map user with employee
        try:
            obj.refresh_from_db()
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step update employee',
                'detail': str(err),
            })
        return obj

    @classmethod
    def create_user(cls, **kwargs):
        try:
            password = kwargs['password']
            ser = UserCreateSerializer(data=kwargs)
            ser.is_valid(raise_exception=True)
            obj = ser.save()
            obj.set_password(password)
            obj.save()
            return obj
        except serializers.ValidationError as err:
            err.detail['step'] = [ErrorDetail(string='In step setup user')]
            raise err
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step setup user',
                'detail': str(err),
            })

    @classmethod
    def update_user(cls, obj, **kwargs):
        try:
            obj.refresh_from_db()
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step update user',
                'detail': str(err),
            })
        return obj

    @classmethod
    def create_space_employee(cls, emp_obj, space_obj, **kwargs):
        try:
            ser = EmployeeSpaceCreateSerializer(data={
                **kwargs,
                'space': space_obj.id,
                'employee': emp_obj.id,
            })
            ser.is_valid(raise_exception=True)
            return ser.save()
        except serializers.ValidationError as err:
            err.detail['step'] = [ErrorDetail(string='In step put employee to space')]
            raise err
        except Exception as err:
            raise serializers.ValidationError({
                'step': 'In step put employee to space',
                'detail': str(err),
            })

    @classmethod
    def check_and_create_plan(cls, plan_data):
        result = []
        for plan in plan_data:
            plan_code = plan.get('code', None)
            plan_title = plan.get('title', None)
            plan_obj = SubscriptionPlan.objects.filter(code=plan_code).first()
            if not plan_obj:
                plan_obj = SubscriptionPlan.objects.create(**{
                    'title': plan_title,
                    'code': plan_code,
                })
                if plan_obj:
                    result.append(plan_obj)
            else:
                result.append(plan_obj)
        return result

    @classmethod
    def create_tenant_plan(cls, plan_obj_list, tenant_obj):
        if plan_obj_list and tenant_obj:
            tenant_plan_json = {}
            bulk_info = []
            if tenant_obj.plan:
                tenant_plan_json = tenant_obj.plan
                tenant_plan_json = json.loads(tenant_plan_json)
            if tenant_plan_json:
                for tenant_plan in tenant_plan_json:
                    is_limited = tenant_plan.get('is_limited', None)
                    license_quantity = tenant_plan.get('quantity', None)
                    plan = SubscriptionPlan.objects.get(code=tenant_plan.get('code', None))
                    purchase_order = tenant_plan.get('purchase_order', None)
                    date_active = tenant_plan.get('date_active', None)
                    date_end = tenant_plan.get('date_end', None)
                    if plan:
                        bulk_info.append(TenantPlan(
                            **{
                                'date_active': date_active,
                                'date_end': date_end,
                                'tenant': tenant_obj,
                                'plan': plan,
                                'is_limited': is_limited,
                                'license_quantity': license_quantity,
                                'license_used': 0,
                                'purchase_order': purchase_order
                            },
                        ))
            if bulk_info:
                TenantPlan.objects.bulk_create(bulk_info)
        return True
