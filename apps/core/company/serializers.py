import random
from rest_framework import serializers
from apps.core.company.models import Company, CompanyUserEmployee
from apps.core.account.models import User
# from apps.core.tenant.models import Tenant
from apps.core.hr.models import Employee
from apps.shared import DisperseModel


# Company Serializer
class CompanyListSerializer(serializers.ModelSerializer):
    tenant_auto_create_company = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'representative_fullname',
            'tenant_auto_create_company',
        )

    @classmethod
    def get_tenant_auto_create_company(cls, obj):
        return obj.tenant.auto_create_company


class CompanyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'representative_fullname',
            'email',
            'address',
            'phone'
        )


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )


class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )


class CompanyOverviewSerializer(serializers.ModelSerializer):
    license_used = serializers.SerializerMethodField()
    power_user = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    employee_linked_user = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'license_used',
            'total_user',
            'power_user',
            'employee',
            'employee_linked_user',

            # 'all_total_user',
            # 'all_power_user',
            # 'all_employee'
        )

    @classmethod
    def get_license_used(cls, obj):
        return [
                {'key': 'Hrm', 'quantity': random.randrange(20, 50, 3)},
                {'key': 'Sale', 'quantity': random.randrange(20, 50, 3)},
                {'key': 'Personal', 'quantity': random.randrange(20, 50, 3)},
                {'key': 'E-office', 'quantity': random.randrange(20, 50, 3)},
        ]

    @classmethod
    def get_power_user(cls, obj):
        return User.objects.filter(company_current=obj.id).filter(is_superuser=1).count()

    @classmethod
    def get_employee(cls, obj):
        return CompanyUserEmployee.object_normal.filter(company=obj.id).count()

    @classmethod
    def get_employee_linked_user(cls, obj):
        return CompanyUserEmployee.object_normal.filter(company=obj.id).exclude(user_id__isnull=True).count()


# Company Map User Employee
class CompanyUserNotMapEmployeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CompanyUserEmployee
        fields = (
            'id',
            'user'
        )

    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'email': obj.user.email,
                'phone': obj.user.phone,
                'full_name': User.get_full_name(obj.user, 2),
            }
        return {}


class CompanyOverviewDetailDataSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = CompanyUserEmployee
        fields = (
            "employee",
            "user",
        )

    def get_employee(self, obj):
        license_list = []
        if obj.employee:
            plan_list = obj.employee.plan.all()
            if plan_list:
                for plan in plan_list:
                    license_list.append({
                        'id': plan.id,
                        'title': plan.title,
                        'code': plan.code
                    })
            return {
                'id': obj.employee.id,
                'full_name': Employee.get_full_name(obj.employee, 2),
                'code': obj.employee.code,
                'license_list': license_list
            }
        return {}

    def get_user(self, obj):
        company_list = []
        if obj.user:
            company_user_list = CompanyUserEmployee.object_normal.select_related('company').filter(
                user=obj.user
            )
            if company_user_list:
                for company_user in company_user_list:
                    company_list.append({
                        'id': company_user.company.id,
                        'title': company_user.company.title,
                        'code': company_user.company.code,
                        'is_created_company': company_user.is_created_company
                    })
            return {
                'id': obj.user.id,
                'full_name': User.get_full_name(obj.user, 2),
                'username': obj.user.username,
                'company_list': company_list
            }
        return {}


class CompanyOverviewDetailSerializer(serializers.ModelSerializer):
    company_data = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "title",
            "company_data",
        )

    def get_company_data(self, obj):
        return CompanyOverviewDetailDataSerializer(
            CompanyUserEmployee.object_normal.select_related(
                'user',
                'employee'
            ).filter(company=obj),
            many=True
        ).data
