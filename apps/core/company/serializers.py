import random

from rest_framework import serializers

from apps.core.company.models import Company
from apps.shared import APIMsg
# from apps.core.tenant.models import Tenant
# from apps.core.hr.models import Employee


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

    @classmethod
    def get_license_used(cls, obj):
        try:
            return [
                {'key': 'Hrm', 'quantity': 10},
                {'key': 'Sale', 'quantity': 15},
                {'key': 'Personal', 'quantity': 30},
                {'key': 'E-office', 'quantity': 20},
            ]
        except Exception as e:
            raise serializers.ValidationError("License used does not exist.")

    @classmethod
    def get_power_user(cls, obj):
        try:
            return 2
        except Exception as e:
            raise serializers.ValidationError("Power user used does not exist.")

    @classmethod
    def get_employee(cls, obj):
        try:
            return 18
        except Exception as e:
            raise serializers.ValidationError("Employee used does not exist.")

    @classmethod
    def get_employee_linked_user(cls, obj):
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
