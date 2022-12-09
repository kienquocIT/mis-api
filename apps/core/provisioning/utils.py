from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from apps.shared import ProvisioningMsg

from apps.core.tenant.models import Tenant

from .serializers import (
    TenantCreateSerializer, CompanyCreateSerializer, SpaceCreateSerializer, EmployeeCreateSerializer,
    UserCreateSerializer, EmployeeSpaceCreateSerializer
)


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
        ...

    def setup_new(
            self, tenant_code,
            tenant_data: dict,
            employee_data: dict,
            user_data: dict,
    ) -> serializers.ValidationError or bool:
        try:
            with transaction.atomic():
                tenant_obj = self.get_tenant_by_code(tenant_code)
                if not tenant_obj:
                    tenant_obj = self.create_tenant(
                        **tenant_data,
                        code=tenant_code,
                    )
                    company_obj = self.create_company(
                        title=tenant_obj.title,
                        code=f'{tenant_obj.code}01',
                        tenant=tenant_obj.id,
                    )
                    space_obj = self.create_space(
                        title='Global',
                        code=f'{tenant_code.upper()} Global',
                        tenant=tenant_obj.id,
                        company=company_obj.id,
                        is_system=True,
                    )
                    employee_obj = self.create_employee(
                        **employee_data,
                        tenant=tenant_obj.id,
                        company=company_obj.id,
                        space=space_obj.id,
                        user=None,
                    )
                    user_obj = self.create_user(
                        **user_data,
                        username_auth=get_user_model().convert_username_field_data(user_data['username'], tenant_obj),
                        first_name=employee_obj.first_name,
                        last_name=employee_obj.last_name,
                        phone=employee_obj.phone,
                        email=employee_obj.email,
                        is_admin_tenant=True,
                        tenant_current=tenant_obj.id,
                        company_current=company_obj.id,
                        employee_current=employee_obj.id,
                        space_current=space_obj.id,
                    )
                    self.update_tenant(
                        tenant_obj,
                        admin_info={
                            'fullname': f'{user_obj.first_name} {user_obj.last_name}',
                            'phone_number': str(user_obj.phone),
                            'username': str(user_obj.username),
                            'email': str(user_obj.email),
                        },
                        admin_created=True,
                        admin=user_obj
                    )
                    self.update_employee(employee_obj, user=user_obj)
                    self.create_space_employee(employee_obj, space_obj, **{})
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
            return ser.save()
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
