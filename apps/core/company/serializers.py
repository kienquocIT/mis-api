import random

from rest_framework import serializers

from apps.core.company.models import Company, CompanyUserEmployee
from apps.core.tenant.models import Tenant
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

    def get_tenant_auto_create_company(self, obj):
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


class TenantInformationSerializer(serializers.ModelSerializer):
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
            'date_created',
            'representative_fullname',
            'total_user',
            'license_used',
            'power_user',
            'employee',
            'employee_linked_user'
        )

    def get_license_used(self, obj):
        try:
            return [
                {'key': 'Hrm', 'quantity': 10},
                {'key': 'Sale', 'quantity': 10}
            ]
        except Exception as e:
            raise serializers.ValidationError("License used does not exist.")

    def get_power_user(self, obj):
        try:
            return 2
        except Exception as e:
            raise serializers.ValidationError("Power user used does not exist.")

    def get_employee(self, obj):
        try:
            return 18
        except Exception as e:
            raise serializers.ValidationError("Employee used does not exist.")

    def get_employee_linked_user(self, obj):
        try:
            return 4
        except Exception as e:
            raise serializers.ValidationError("Employee linked user used does not exist.")


class CompanyOverviewSerializer(serializers.ModelSerializer):
    license_used = serializers.SerializerMethodField()
    total_user = serializers.SerializerMethodField()
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
            'employee_linked_user'
        )

    @classmethod
    def get_license_used(cls, obj):
        return {
            'sale': random.randrange(20, 50, 3),
            'e-office': random.randrange(20, 50, 3),
            'hrm': random.randrange(20, 50, 3),
            'personal': random.randrange(20, 50, 3)
        }

    @classmethod
    def get_total_user(cls, obj):
        return random.randrange(20, 50, 3)

    @classmethod
    def get_power_user(cls, obj):
        return random.randrange(1, 10, 3)

    @classmethod
    def get_employee(cls, obj):
        return random.randrange(20, 50, 3)

    @classmethod
    def get_employee_linked_user(cls, obj):
        return random.randrange(1, 20, 3)


class EmployeeListByCompanyOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUserEmployee
        fields = '__all__'


class EmployeeListByCompanyOverviewSerializer1(serializers.ModelSerializer):
    license = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = DisperseModel(app_model='hr.Employee').get_model()
        fields = (
            'id',
            'code',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'date_joined',
            'user_id',
            'is_active',
            'license',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name()

    @classmethod
    def get_license(cls, obj):
        data = [
            {"id": 1, "code": "sale", "title": "Sale"},
            {"id": 2, "code": "e-office", "title": "E-Office"},
            {"id": 3, "code": "personal", "title": "Personal"},
            {"id": 4, "code": "hrm", "title": "hrm"},
            {"id": 5, "code": "a", "title": "A"},
            {"id": 6, "code": "b", "title": "B"},
            {"id": 7, "code": "c", "title": "C"},
        ]
        stt = random.randrange(0, 4)
        stt2 = random.randrange(5, 7)
        return data[stt:stt2]


class UserListByCompanyOverviewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = DisperseModel(app_model='account.User').get_model()
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
        )

    @classmethod
    def get_full_name(cls, obj):
        return obj.get_full_name()
